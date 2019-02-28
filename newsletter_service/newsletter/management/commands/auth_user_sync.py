import json

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from kafka import KafkaConsumer


class Command(BaseCommand):
    help = "This command is a deamon to work as ACL to auth_user"

    def add_arguments(self, parser):
        parser.add_argument(
            'topic',
            type=str,
            help='Kafka topic',
        )

    def handle(self, *args, **kwargs):
        consumer = KafkaConsumer(
            kwargs['topic'],
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            group_id=None,
        )
        for msg in consumer:
            try:
                user = User(**msg.value['payload']['after'])
                user.save()
            except Exception:
                pass
