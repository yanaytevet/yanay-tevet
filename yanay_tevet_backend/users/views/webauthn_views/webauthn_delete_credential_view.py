from typing import Type

from ninja import Schema, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from users.managers.webauthn_manager import WebAuthnManager
from users.schemas.webauthn_schemas import DeleteCredentialInput, DeleteCredentialOutput


class WebAuthnDeleteCredentialView(SimplePostAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return DeleteCredentialInput

    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return DeleteCredentialOutput

    @classmethod
    async def check_permitted(cls, request: APIRequest, data: DeleteCredentialInput, path: Path = None) -> None:
        await LoginPermissionChecker().async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def run_action(cls, request: APIRequest, data: DeleteCredentialInput, path: Path = None) -> DeleteCredentialOutput:
        user = await request.future_user
        await WebAuthnManager.delete_credential(user, data.credential_id)
        return DeleteCredentialOutput(success=True)

    @classmethod
    def get_tags(cls) -> list[str]:
        return ['Auth/WebAuthn']
