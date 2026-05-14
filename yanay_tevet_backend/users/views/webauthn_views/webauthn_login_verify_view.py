from typing import Type

from ninja import Schema, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from users.managers.django_auth import DjangoAuth
from users.managers.webauthn_manager import WebAuthnManager
from users.schemas.auth_schema import AuthSchema
from users.schemas.webauthn_schemas import LoginVerifyInput
from users.serializers.user.user_serializer import UserSerializer


class WebAuthnLoginVerifyView(SimplePostAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return LoginVerifyInput

    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return AuthSchema

    @classmethod
    async def check_permitted(cls, request: APIRequest, data: LoginVerifyInput, path: Path = None) -> None:
        pass  # public — user is identified via passkey, not prior auth

    @classmethod
    async def run_action(cls, request: APIRequest, data: LoginVerifyInput, path: Path = None) -> AuthSchema:
        user = await WebAuthnManager.verify_login(data)
        await DjangoAuth.async_login(request.response, user)
        return AuthSchema(
            is_authenticated=True,
            user=await UserSerializer().serialize(user),
            access_token=DjangoAuth.create_access_token(user.id),
        )

    @classmethod
    def get_tags(cls) -> list[str]:
        return ['Auth/WebAuthn']
