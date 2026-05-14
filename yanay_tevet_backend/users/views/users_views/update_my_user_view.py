from typing import Type, Optional

from ninja import Schema, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from users.models import User
from users.serializers.user.user_serializer import UserSchema, UserSerializer


class UpdateMyUserInputSchema(Schema):
    first_name: str
    last_name: str
    email: Optional[str] = None


class UpdateMyUserView(SimplePostAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return UserSchema

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return UpdateMyUserInputSchema

    @classmethod
    async def check_permitted(cls, request: APIRequest, data: UpdateMyUserInputSchema, path: Path = None) -> None:
        user = await request.future_user
        await LoginPermissionChecker().async_raise_exception_if_not_valid(user)

    @classmethod
    async def run_action(cls, request: APIRequest, data: UpdateMyUserInputSchema, path: Path = None) -> UserSchema:
        user: User = await request.future_user
        user.first_name = data.first_name
        user.last_name = data.last_name
        if data.email is not None:
            email = data.email.strip().lower()
            email_taken = await User.objects.filter(email=email).exclude(id=user.id).aexists()
            if email_taken:
                raise RestAPIException(
                    status_code=StatusCode.HTTP_400_BAD_REQUEST,
                    message='This email address is already in use.',
                    error_code='email_taken',
                )
            user.email = email
        await user.asave()
        return await UserSerializer().serialize(user)
