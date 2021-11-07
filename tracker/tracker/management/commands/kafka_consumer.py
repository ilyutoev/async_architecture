import json
import uuid

from django.conf import settings
from kafka import KafkaConsumer
from django.core.management.base import BaseCommand

from authn.models import Account


class Command(BaseCommand):

    def handle(self, *args, **options):
        consumer = KafkaConsumer(
            settings.ACCOUNTS_STREAM_TOPIC,
            settings.ACCOUNTS_TOPIC,
            bootstrap_servers=settings.KAFKA_URL,
            group_id='tracker-service',
            value_deserializer=json.loads
        )
        for msg in consumer:
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
