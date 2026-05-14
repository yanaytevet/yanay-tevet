from django.conf import settings
from django.db import models
from django.utils import timezone


class WebAuthnChallenge(models.Model):
    CHALLENGE_TTL_SECONDS = 300  # 5 minutes

    challenge = models.CharField(max_length=512, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='webauthn_challenges',
    )
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'users'

    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at
