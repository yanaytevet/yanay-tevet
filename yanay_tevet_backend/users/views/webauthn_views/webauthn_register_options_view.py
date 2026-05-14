from typing import Type

from ninja import Schema, Query, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from users.managers.webauthn_manager import WebAuthnManager
from users.schemas.webauthn_schemas import RegistrationOptionsSchema


class WebAuthnRegisterOptionsView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return RegistrationOptionsSchema

    @classmethod
    async def check_permitted(cls, request: APIRequest, query: Query = None, path: Path = None) -> None:
        await LoginPermissionChecker().async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def get_data(cls, request: APIRequest, query: Query = None, path: Path = None) -> RegistrationOptionsSchema:
        return await WebAuthnManager.generate_register_options(await request.future_user)

    @classmethod
    def get_tags(cls) -> list[str]:
        return ['Auth/WebAuthn']
