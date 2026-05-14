from typing import Type

from ninja import Schema, Query, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from users.managers.webauthn_manager import WebAuthnManager
from users.schemas.webauthn_schemas import LoginOptionsSchema


class WebAuthnLoginOptionsView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return LoginOptionsSchema

    @classmethod
    async def check_permitted(cls, request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass  # public — no authentication required

    @classmethod
    async def get_data(cls, request: APIRequest, query: Query = None, path: Path = None) -> LoginOptionsSchema:
        return await WebAuthnManager.generate_login_options()

    @classmethod
    def get_tags(cls) -> list[str]:
        return ['Auth/WebAuthn']
