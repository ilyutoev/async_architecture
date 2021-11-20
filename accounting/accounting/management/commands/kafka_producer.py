import json
from datetime import date

from django.conf import settings
from django.core.management import BaseCommand
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_URL,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


class Command(BaseCommand):

    def handle(self, *args, **options):
        event = {
            'event_name': 'SchedulerDayOff',
            'version': 'v1',
            'data': {
                'now': str(date.today())
            }
        }
        producer.send(
            topic=settings.SCHEDULER_TOPIC,
            value=event
        )
