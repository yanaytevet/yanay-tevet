from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'example command'

    def handle(self, *args, **options) -> None:
        pass