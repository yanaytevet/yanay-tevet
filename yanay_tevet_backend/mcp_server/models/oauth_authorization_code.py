from typing import TYPE_CHECKING

from django.db import models

from mcp_server.models.oauth_client import OAuthClient
from users.models import User


class OAuthAuthorizationCode(models.Model):
    """A short-lived authorization code issued by /oauth/authorize and redeemed at /oauth/token.

    The raw code is never stored; only its SHA-256 hash (`code_hash`) is kept.
    """

    if TYPE_CHECKING:
        id: int
        client_id: int
        user_id: int

    code_hash = models.CharField(max_length=64, unique=True)
    client = models.ForeignKey(OAuthClient, on_delete=models.CASCADE, related_name='authorization_codes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mcp_authorization_codes')
    redirect_uri = models.TextField()
    scope = models.CharField(max_length=255, blank=True, default='')
    resource = models.TextField(blank=True, default='')
    code_challenge = models.CharField(max_length=255, blank=True, default='')
    code_challenge_method = models.CharField(max_length=16, blank=True, default='')
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'OAuthAuthorizationCode(client={self.client_id}, user={self.user_id})'
