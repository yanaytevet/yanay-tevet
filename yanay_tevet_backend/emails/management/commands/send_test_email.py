from django.core.management.base import BaseCommand

from emails.email_templates.test_email import TestEmail, TestEmailContext


class Command(BaseCommand):
    help = 'Send a test email to one or more addresses'

    def add_arguments(self, parser):
        parser.add_argument('email_addresses', nargs='+', type=str, help='Recipient email address(es)')
        parser.add_argument('--message', type=str, default='', help='Optional custom message to include')

    def handle(self, *args, **options) -> None:
        addresses = options['email_addresses']
        context = TestEmailContext(message=options['message'])
        email = TestEmail()

        for address in addresses:
            self.stdout.write(f'Sending test email to {address}...')
            email.send_to_address(context=context, email_address=address)
            self.stdout.write(self.style.SUCCESS(f'  ✓ Sent to {address}'))
