import json
import uuid

from django.conf import settings
from kafka import KafkaConsumer
from django.core.management.base import BaseCommand

from authn.models import Account
from analitycs.models import Task
from analitycs.models import AuditLog
from analitycs.models import Status


class Command(BaseCommand):

    def handle(self, *args, **options):
        consumer = KafkaConsumer(
            settings.ACCOUNTS_STREAM_TOPIC,
            settings.ACCOUNTS_TOPIC,
            settings.TASKS_STREAM_TOPIC,
            settings.TASKS_TOPIC,
            settings.AUDIT_LOG_STREAM_TOPIC,
            bootstrap_servers=settings.KAFKA_URL,
            group_id='analytics-service',
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

                task = Task.objects.filter(public_id=public_id).first()
                if task:
                    task.description = description
                    task.jira_id = jira_id
                    task.save()
                else:
                    Task.objects.create(
                        public_id=public_id,
                        description=description,
                        jira_id=jira_id,
                    )

            if event_name == 'TaskAssigned':
                task_public_id = event.get('data', {}).get('public_id')
                account_public_id = event.get('data', {}).get('account_public_id')

                account = Account.objects.filter(public_id=account_public_id).first()
                task = Task.objects.filter(public_id=task_public_id).first()
                if not task:
                    task = Task.objects.create(public_id=task_public_id)

                if account and task:
                    task.account = account
                    task.save()

            if event_name == 'TaskCompleted':
                task_public_id = event.get('data', {}).get('public_id')

                task = Task.objects.filter(public_id=task_public_id).first()

                if task:
                    task.status = Status.DONE
                    task.save()

            if event_name == 'AuditLogCreated':
                public_id = event.get('data', {}).get('public_id')
                account_public_id = event.get('data', {}).get('account_public_id')
                debit = event.get('data', {}).get('debit')
                credit = event.get('data', {}).get('credit')
                task_public_id = event.get('data', {}).get('task_public_id')
                status = event.get('data', {}).get('status')

                account = Account.objects.filter(public_id=account_public_id).first()
                task = Task.objects.filter(public_id=task_public_id).first()

                AuditLog.objects.create(
                    public_id=public_id,
                    account=account,
                    debit=debit,
                    credit=credit,
                    task=task,
                    status=status
                )
