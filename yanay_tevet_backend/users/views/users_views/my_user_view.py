from ninja import Query, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.read_views.read_item_api_view import ReadItemAPIView
from users.models import User
from users.serializers.user.user_serializer import UserSerializer


class MyUserItemView(ReadItemAPIView):

    @classmethod
    def get_serializer(cls) -> Serializer:
        return UserSerializer()

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, query: Query, path: Path) -> None:
        user_obj = await request.future_user
        await LoginPermissionChecker().async_raise_exception_if_not_valid(user_obj)

    @classmethod
    async def get_object(cls, request: APIRequest, query: Query, path: Path) -> User:
        return await request.future_user

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: User, query: Query, path: Path) -> None:
        pass
