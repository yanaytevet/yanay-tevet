from typing import Type

from ninja import Schema, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from users.managers.django_auth import DjangoAuth
from users.managers.webauthn_manager import WebAuthnManager
from users.schemas.auth_schema import AuthSchema
from users.schemas.webauthn_schemas import RegistrationVerifyInput
from users.serializers.user.user_serializer import UserSerializer


class WebAuthnRegisterVerifyView(SimplePostAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return RegistrationVerifyInput

    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return AuthSchema

    @classmethod
    async def check_permitted(cls, request: APIRequest, data: RegistrationVerifyInput, path: Path = None) -> None:
        await LoginPermissionChecker().async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def run_action(cls, request: APIRequest, data: RegistrationVerifyInput, path: Path = None) -> AuthSchema:
        user = await request.future_user
        await WebAuthnManager.verify_registration(user, data)
        await DjangoAuth.async_login(request.response, user)
        return AuthSchema(
            is_authenticated=True,
            user=await UserSerializer().serialize(user),
            access_token=DjangoAuth.create_access_token(user.id),
        )

    @classmethod
    def get_tags(cls) -> list[str]:
        return ['Auth/WebAuthn']
