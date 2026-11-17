from typing import Type

from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from users.enums.language import Language
from users.managers.user_language_manager import UserLanguageManager
from users.models import User
from users.serializers.user.user_serializer import UserSchema, UserSerializer


class UpdateMyLanguageInputSchema(Schema):
    language: Language


class UpdateMyLanguageView(SimplePostAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return UserSchema

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return UpdateMyLanguageInputSchema

    @classmethod
    async def check_permitted(cls, request: APIRequest, data: UpdateMyLanguageInputSchema, path: Path = None) -> None:
        user = await request.future_user
        await LoginPermissionChecker().async_raise_exception_if_not_valid(user)

    @classmethod
    async def run_action(cls, request: APIRequest, data: UpdateMyLanguageInputSchema, path: Path = None) -> UserSchema:
        user: User = await request.future_user
        updated = await UserLanguageManager(user).set_language(data.language)
        return await UserSerializer().serialize(updated)
