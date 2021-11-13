import json
import uuid

from accounts.models import Account
from django.conf import settings
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UsernameField
from jsonschema import validate
from kafka import KafkaProducer

from events_schema import schema

producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_URL,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


class AccountCreationForm(UserCreationForm):
    class Meta:
        model = Account
        fields = ("email",)
        field_classes = {'email': UsernameField}

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if not user.public_id:
            user.public_id = str(uuid.uuid4())
        if commit:
            user.save()
        return user


class AccountChangeForm(UserChangeForm):
    class Meta:
        model = Account
        fields = ('email', 'role', 'first_name')

    def clean(self):
        event = {
            'event_name': 'AccountUpdated',
            'version': 'v1',
            'data': {
                'public_id': str(self.instance.public_id),
                'email': self.cleaned_data['email'],
                'first_name': self.cleaned_data['first_name'],
            }
        }
        validate(event, schema[event['version']][event['event_name']])
        producer.send(
            topic=settings.ACCOUNTS_STREAM_TOPIC,
            value=event
        )

        if self.instance.role != self.cleaned_data['role']:
            event = {
                'event_name': 'AccountRoleChanged',
                'version': 'v1',
                'data': {
                    'public_id': str(self.instance.public_id),
                    'role': self.cleaned_data['role'],
                }
            }
            validate(event, schema[event['version']][event['event_name']])
            producer.send(
                topic=settings.ACCOUNTS_TOPIC,
                value=event
            )
