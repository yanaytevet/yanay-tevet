from typing import TYPE_CHECKING

from django.db import models

from mcp_server.models.oauth_client import OAuthClient
from users.models import User


class OAuthRefreshToken(models.Model):
    """A refresh token used to mint new access tokens without re-consent.

    The raw token is never stored; only its SHA-256 hash (`token_hash`) is kept.
    Rotated on every use.
    """

    if TYPE_CHECKING:
        id: int
        client_id: int
        user_id: int

    token_hash = models.CharField(max_length=64, unique=True)
    client = models.ForeignKey(OAuthClient, on_delete=models.CASCADE, related_name='refresh_tokens')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mcp_refresh_tokens')
    scope = models.CharField(max_length=255, blank=True, default='')
    resource = models.TextField(blank=True, default='')
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'OAuthRefreshToken(client={self.client_id}, user={self.user_id})'
