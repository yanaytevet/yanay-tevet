from common.django_utils.api_router_creator import ApiRouterCreator
from users.views.auth_views.auth_view import AuthView
from users.views.auth_views.google_login_view import GoogleLoginView
from users.views.auth_views.change_password_views import ChangePasswordView
from users.views.auth_views.login_view import LoginView
from users.views.auth_views.logout_view import LogoutView
from users.views.forgot_my_password_views.change_password_by_access_id_view import ChangePasswordByAccessIdView
from users.views.forgot_my_password_views.check_temporary_access_view import CheckTemporaryAccessView
from users.views.forgot_my_password_views.forgot_my_password_view import ForgotMyPasswordView
from users.views.webauthn_views.webauthn_credentials_view import WebAuthnCredentialsView
from users.views.webauthn_views.webauthn_delete_credential_view import WebAuthnDeleteCredentialView
from users.views.webauthn_views.webauthn_login_options_view import WebAuthnLoginOptionsView
from users.views.webauthn_views.webauthn_login_verify_view import WebAuthnLoginVerifyView
from users.views.webauthn_views.webauthn_register_options_view import WebAuthnRegisterOptionsView
from users.views.webauthn_views.webauthn_register_verify_view import WebAuthnRegisterVerifyView

api, router = ApiRouterCreator.create_api_and_router('auth')

AuthView.register_get(router, '')
LoginView.register_post(router, 'login/')
GoogleLoginView.register_post(router, 'google-login/')
LogoutView.register_post(router, 'logout/')
ChangePasswordView.register_post(router, 'change-password/')

CheckTemporaryAccessView.register_post(router, 'check-temporary-access/')
ForgotMyPasswordView.register_post(router, 'forgot-my-password/')
ChangePasswordByAccessIdView.register_post(router, 'change-password-by-access-id/')

WebAuthnRegisterOptionsView.register_get(router, 'webauthn/register-options/')
WebAuthnRegisterVerifyView.register_post(router, 'webauthn/register-verify/')
WebAuthnLoginOptionsView.register_get(router, 'webauthn/login-options/')
WebAuthnLoginVerifyView.register_post(router, 'webauthn/login-verify/')
WebAuthnCredentialsView.register_get(router, 'webauthn/credentials/')
WebAuthnDeleteCredentialView.register_post(router, 'webauthn/delete-credential/')
