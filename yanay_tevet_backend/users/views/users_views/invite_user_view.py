from typing import Type

from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from users.enums.permissions import Permissions
from users.managers.invitation_manager import InvitationManager
from users.models import User
from users.permissions_checkers.admin_permissions_checker import AdminPermissionsChecker


class InviteUserInputSchema(Schema):
    email: str
    permissions: list[Permissions] = []


class InviteUserOutput(Schema):
    applied_immediately: bool


class InviteUserView(SimplePostAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return InviteUserOutput

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return InviteUserInputSchema

    @classmethod
    async def check_permitted(cls, request: APIRequest, data: InviteUserInputSchema, path: Path = None) -> None:
        user = await request.future_user
        await AdminPermissionsChecker().async_raise_exception_if_not_valid(user)

    @classmethod
    async def run_action(cls, request: APIRequest, data: InviteUserInputSchema, path: Path = None) -> InviteUserOutput:
        acting_user: User = await request.future_user
        result = await InvitationManager(acting_user).invite(data.email, data.permissions)
        return InviteUserOutput(applied_immediately=result.applied_immediately)
