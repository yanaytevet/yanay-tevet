from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from users.models import User


class EmailManager:
    @classmethod
    async def send_template_to_users(
        cls,
        template_name: str,
        subject: str,
        context: dict,
        users: list[User],
    ) -> None:
        for user in users:
            if not user.email:
                continue
            if user.is_unsubscribed:
                continue
            cls.send_template_to_address(
                template_name=template_name,
                subject=subject,
                context={**context, 'user': user},
                email_address=user.email,
            )

    @classmethod
    def generate_email_html(cls, template_name: str, context: dict) -> str:
        full_context = {
            'frontend_url': settings.FRONTEND_URL,
            **context,
        }
        return render_to_string(f'emails/{template_name}.html', full_context)

    @classmethod
    def send_email_html(cls, html: str, subject: str, email_address: str) -> None:
        from_email = f'{settings.EMAIL_FROM_NAME} <{settings.DEFAULT_FROM_EMAIL}>'
        msg = EmailMultiAlternatives(
            subject=subject,
            body='',
            from_email=from_email,
            to=[email_address],
        )
        msg.attach_alternative(html, 'text/html')
        msg.send()

    @classmethod
    def send_template_to_address(
        cls,
        template_name: str,
        subject: str,
        context: dict,
        email_address: str,
    ) -> None:
        html = cls.generate_email_html(template_name, context)
        cls.send_email_html(html, subject, email_address)
