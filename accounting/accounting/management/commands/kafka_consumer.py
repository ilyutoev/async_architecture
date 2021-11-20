import json
import uuid
import random

from django.conf import settings
from django.db import transaction
from kafka import KafkaConsumer
from django.core.management.base import BaseCommand

from authn.models import Account
from authn.models import Role
from accounting.models import Task
from accounting.models import AuditLog
from accounting.models import Status
from accounting.models import AuditLogStatus


class Command(BaseCommand):

    def handle(self, *args, **options):
        consumer = KafkaConsumer(
            settings.ACCOUNTS_STREAM_TOPIC,
            settings.ACCOUNTS_TOPIC,
            settings.TASKS_STREAM_TOPIC,
            settings.TASKS_TOPIC,
            settings.SCHEDULER_TOPIC,
            bootstrap_servers=settings.KAFKA_URL,
            group_id='accounting-service',
            value_deserializer=json.loads,
        )
        for msg in consumer:
            print(msg)
            event = msg.value
            event_name = event.get('event_name')

            if event_name == 'AccountCreated':
                public_id = event.get('data', {}).get('public_id')
                email = event.get('data', {}).get('email')
                role = event.get('data', {}).get('role')
                first_name = event.get('data', {}).get('first_name')

                if any((public_id, email, role)):
                    account = Account.objects.filter(public_id=public_id).first()
                    if account is None:
                        Account.objects.create_user(
                            email=email,
                            password=str(uuid.uuid4()),
                            first_name=first_name,
                            public_id=public_id,
                            role=role,
                        )

            if event_name == 'AccountUpdated':
                public_id = event.get('data', {}).get('public_id')
                email = event.get('data', {}).get('email')
                first_name = event.get('data', {}).get('first_name')

                Account.objects.filter(
                    public_id=public_id
                ).update(
                    email=email,
                    first_name=first_name
                )

            if event_name == 'AccountDeleted':
                public_id = event.get('data', {}).get('public_id')

                Account.objects.filter(
                    public_id=public_id
                ).update(
                    is_active=False
                )

            if event_name == 'AccountRoleChanged':
                public_id = event.get('data', {}).get('public_id')
                role = event.get('data', {}).get('role')

                Account.objects.filter(
                    public_id=public_id
                ).update(
                    role=role
                )

            if event_name == 'TaskCreated':
                public_id = event.get('data', {}).get('public_id')
                description = event.get('data', {}).get('description')
                jira_id = event.get('data', {}).get('jira_id')
                price = random.randint(10, 20)

                task = Task.objects.filter(public_id=public_id).first()
                if task:
                    task.description = description
                    task.jira_id = jira_id
                    if not task.price:
                        task.price = price
                    task.save()
                else:
                    Task.objects.create(
                        public_id=public_id,
                        description=description,
                        jira_id=jira_id,
                        price=price
                    )

            if event_name == 'TaskAssigned':
                task_public_id = event.get('data', {}).get('public_id')
                account_public_id = event.get('data', {}).get('account_public_id')

                account = Account.objects.filter(public_id=account_public_id).first()
                task = Task.objects.filter(public_id=task_public_id).first()
                if not task:
                    task = Task.objects.create(public_id=task_public_id)

                if account and task:
                    with transaction.atomic():
                        task.account = account
                        if not task.price:
                            task.price = random.randint(10, 20)
                        task.save()

                        account.balance -= task.price
                        account.save()

                        AuditLog.objects.create(
                            public_id=uuid.uuid4(),
                            account=account,
                            debit=task.price,
                            credit=0,
                            task=task,
                            status=AuditLogStatus.TASK_ASSIGNED
                        )

            if event_name == 'TaskCompleted':
                task_public_id = event.get('data', {}).get('public_id')

                task = Task.objects.filter(public_id=task_public_id).first()

                completed_price = random.randint(20, 40)
                if task:
                    task.account.balance += completed_price
                    task.account.save()

                    task.status = Status.DONE
                    task.save()

                    AuditLog.objects.create(
                        public_id=uuid.uuid4(),
                        account=task.account,
                        debit=0,
                        credit=completed_price,
                        task=task,
                        status=AuditLogStatus.TASK_COMPLETED
                    )

            if event_name == 'SchedulerDayOff':
                with transaction.atomic():
                    for worker in Account.objects.filter(role=Role.WORKER):
                        if worker.balance > 0:
                            AuditLog.objects.create(
                                public_id=uuid.uuid4(),
                                account=worker,
                                debit=worker.balance,
                                credit=0,
                                status=AuditLogStatus.PAY_DAY
                            )
                            worker.balance = 0
                            worker.save()
