from typing import Type

from ninja import Schema, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from users.enums.permissions import Permissions
from users.managers.user_permissions_manager import UserPermissionsManager
from users.models import User
from users.permissions_checkers.admin_permissions_checker import AdminPermissionsChecker
from users.serializers.user.admin_user_serializer import AdminUserOutput, AdminUserSerializer


class UpdateUserPermissionsInputSchema(Schema):
    user_id: int
    permissions: list[Permissions]


class UpdateUserPermissionsView(SimplePostAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return AdminUserOutput

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return UpdateUserPermissionsInputSchema

    @classmethod
    async def check_permitted(cls, request: APIRequest, data: UpdateUserPermissionsInputSchema,
                              path: Path = None) -> None:
        user = await request.future_user
        await AdminPermissionsChecker().async_raise_exception_if_not_valid(user)

    @classmethod
    async def run_action(cls, request: APIRequest, data: UpdateUserPermissionsInputSchema,
                         path: Path = None) -> AdminUserOutput:
        acting_user: User = await request.future_user
        updated_user = await UserPermissionsManager(acting_user).set_permissions(data.user_id, data.permissions)
        return await AdminUserSerializer().serialize(updated_user)
