from django.contrib import admin

from mcp_server.models.oauth_access_token import OAuthAccessToken
from mcp_server.models.oauth_authorization_code import OAuthAuthorizationCode
from mcp_server.models.oauth_client import OAuthClient
from mcp_server.models.oauth_refresh_token import OAuthRefreshToken


@admin.register(OAuthClient)
class OAuthClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'client_id', 'client_name', 'token_endpoint_auth_method', 'created_at']
    search_fields = ['client_id', 'client_name']


@admin.register(OAuthAccessToken)
class OAuthAccessTokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'user', 'expires_at', 'revoked', 'last_used_at']
    list_filter = ['revoked']
    raw_id_fields = ['client', 'user']


@admin.register(OAuthRefreshToken)
class OAuthRefreshTokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'user', 'expires_at', 'revoked']
    list_filter = ['revoked']
    raw_id_fields = ['client', 'user']


@admin.register(OAuthAuthorizationCode)
class OAuthAuthorizationCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'user', 'expires_at', 'used']
    list_filter = ['used']
    raw_id_fields = ['client', 'user']
