from unittest.mock import AsyncMock, patch

from django.test import AsyncClient, TestCase

from common.simple_api.exceptions.rest_api_exception import RestAPIException
from users.models import User
from users.views.auth_views.google_login_view import GoogleLoginSchema, GoogleLoginView


def google_id_info(email: str, email_verified: bool) -> dict:
    return {'email': email, 'email_verified': email_verified, 'given_name': 'Given', 'family_name': 'Family'}


class GoogleLoginTest(TestCase):
    """Google sign-in matches an existing account by email address, so the address has to be one
    Google verified, and the account it lands on has to be active."""

    @classmethod
    def setUpTestData(cls) -> None:
        User.objects.create(username='active@example.com', email='active@example.com')
        User.objects.create(username='inactive@example.com', email='inactive@example.com', is_active=False)

    async def sign_in(self, id_info: dict) -> None:
        with patch.object(GoogleLoginView, '_exchange_code_for_id_token', AsyncMock(return_value='id-token')), \
                patch('users.views.auth_views.google_login_view.id_token.verify_oauth2_token', return_value=id_info):
            await GoogleLoginView.run_action(None, GoogleLoginSchema(google_code='code'))

    async def test_an_unverified_address_is_refused(self) -> None:
        with self.assertRaises(RestAPIException) as raised:
            await self.sign_in(google_id_info('active@example.com', email_verified=False))
        self.assertEqual(raised.exception.error_code, 'invalid_google_token')

    async def test_an_inactive_account_is_refused(self) -> None:
        with self.assertRaises(RestAPIException) as raised:
            await self.sign_in(google_id_info('inactive@example.com', email_verified=True))
        self.assertEqual(raised.exception.error_code, 'user_is_inactive')

    async def test_a_verified_address_of_an_active_account_signs_in(self) -> None:
        with patch.object(GoogleLoginView, '_exchange_code_for_id_token', AsyncMock(return_value='id-token')), \
                patch('users.views.auth_views.google_login_view.id_token.verify_oauth2_token',
                      return_value=google_id_info('active@example.com', email_verified=True)):
            response = await AsyncClient().post(
                '/auth/google-login/', {'google_code': 'code'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIs(response.json()['is_authenticated'], True)
