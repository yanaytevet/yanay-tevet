from typing import Type

from ninja import Schema, Path, UploadedFile

from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.views.upload_files_views.upload_files_view import UploadFilesView
from users.managers.user_profile_image_manager import UserProfileImageManager
from users.models import User
from users.serializers.user.user_serializer import UserSchema, UserSerializer


class UploadUserProfileImageView(UploadFilesView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return UserSchema

    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return Schema

    @classmethod
    async def check_permitted(cls, request: APIRequest, path: Path) -> None:
        await LoginPermissionChecker().async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def run_action(cls, api_request: APIRequest, files: list[UploadedFile], path: Path = None) -> UserSchema:
        user: User = await api_request.future_user
        await UserProfileImageManager.upload_profile_image(user, files[0])
        return await UserSerializer().serialize(user)
