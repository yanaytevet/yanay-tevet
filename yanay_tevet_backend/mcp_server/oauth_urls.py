from django.urls import path

from mcp_server.oauth.authorize_view import authorize
from mcp_server.oauth.metadata_views import (
    authorization_server_metadata,
    protected_resource_metadata,
)
from mcp_server.oauth.register_view import register_client
from mcp_server.oauth.revoke_view import revoke
from mcp_server.oauth.token_view import token

# Mounted at the site root so the well-known metadata sits at the expected discovery paths.
urlpatterns = [
    path('.well-known/oauth-authorization-server', authorization_server_metadata),
    path('.well-known/oauth-protected-resource', protected_resource_metadata),
    path('oauth/authorize', authorize),
    path('oauth/token', token),
    path('oauth/register', register_client),
    path('oauth/revoke', revoke),
]
