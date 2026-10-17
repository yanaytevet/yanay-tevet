import json
from datetime import timedelta

from django.test import AsyncClient, TestCase
from django.utils import timezone
from webauthn.helpers import bytes_to_base64url

from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.testing.authenticated_client import AuthenticatedClient
from mcp_server.managers.oauth_manager import OAuthManager
from mcp_server.models.oauth_client import OAuthClient
from users.managers.django_auth import DjangoAuth
from users.managers.webauthn_manager import WebAuthnManager
from users.models import User
from users.models.webauthn_challenge import WebAuthnChallenge
from users.models.webauthn_credential import WebAuthnCredential
from users.schemas.webauthn_schemas import AssertionResponseInput, LoginVerifyInput


class DeactivatedUserTest(TestCase):
    """A token stays valid for its whole lifetime whatever happens to the account behind it, so every
    way in has to check `is_active`, or deactivating a user waits for their tokens to expire. Each test
    runs the same path for an active user too, so a refusal is known to come from `is_active`."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.active_user = User.objects.create(username='active@example.com', email='active@example.com')
        cls.inactive_user = User.objects.create(
            username='inactive@example.com', email='inactive@example.com', is_active=False)

    async def test_an_access_token_no_longer_resolves_to_the_user(self) -> None:
        for user, expected in ((self.active_user, self.active_user), (self.inactive_user, None)):
            token = DjangoAuth.create_access_token(user.id)
            self.assertEqual(await DjangoAuth.get_user_from_access_token(token), expected)

    async def test_an_api_request_with_their_access_token_is_refused(self) -> None:
        response = await AuthenticatedClient(self.active_user).get('/api/users/my/')
        self.assertEqual(response.status_code, 200)

        response = await AuthenticatedClient(self.inactive_user).get('/api/users/my/')
        self.assertEqual(response.status_code, 401)

    async def test_their_refresh_cookie_mints_no_access_token(self) -> None:
        for user, expected in ((self.active_user, True), (self.inactive_user, False)):
            client = AsyncClient()
            client.cookies[DjangoAuth.REFRESH_TOKEN_KEY] = DjangoAuth.create_refresh_token(user.id)
            response = await client.get('/auth/')
            self.assertEqual(response.status_code, 200)
            self.assertIs(response.json()['is_authenticated'], expected)

    async def test_passkey_login_is_refused(self) -> None:
        raw_id = b'passkey-of-an-inactive-user'
        await WebAuthnChallenge.objects.acreate(
            challenge='the-challenge', user=None, expires_at=timezone.now() + timedelta(minutes=5))
        await WebAuthnCredential.objects.acreate(
            user=self.inactive_user, credential_id=bytes_to_base64url(raw_id), public_key=b'', user_handle='')
        client_data = json.dumps({'challenge': 'the-challenge'}).encode()
        data = LoginVerifyInput(
            id=bytes_to_base64url(raw_id),
            rawId=bytes_to_base64url(raw_id),
            type='public-key',
            response=AssertionResponseInput(
                clientDataJSON=bytes_to_base64url(client_data), authenticatorData='', signature=''),
        )

        with self.assertRaises(RestAPIException) as raised:
            await WebAuthnManager.verify_login(data)
        self.assertEqual(raised.exception.error_code, 'user_is_inactive')

    async def test_mcp_connector_tokens_stop_working(self) -> None:
        client = await OAuthClient.objects.acreate(client_id='test-client')
        for user, works in ((self.active_user, True), (self.inactive_user, False)):
            access_token, _ = await OAuthManager.create_access_token(client, user, scope='', resource='')
            refresh_token = await OAuthManager.create_refresh_token(client, user, scope='', resource='')
            self.assertEqual(await OAuthManager.resolve_access_token(access_token) is not None, works)
            self.assertEqual(await OAuthManager.consume_refresh_token(refresh_token) is not None, works)
