from django.conf import settings
from django.db import models


class WebAuthnCredential(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='webauthn_credentials',
    )
    credential_id = models.TextField(unique=True)  # base64url-encoded
    public_key = models.BinaryField()
    sign_count = models.PositiveIntegerField(default=0)
    user_handle = models.CharField(max_length=255)  # base64url(str(user.id).encode())
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'users'

    def __str__(self) -> str:
        return f'WebAuthnCredential(user_id={self.user_id})'
