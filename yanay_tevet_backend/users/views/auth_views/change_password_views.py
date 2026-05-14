import re
from typing import Type

from ninja import Schema, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from users.managers.django_auth import DjangoAuth
from users.models import User

PASSWORD_MIN_LENGTH = 8


def validate_new_password(password: str) -> None:
    errors = []
    if len(password) < PASSWORD_MIN_LENGTH:
        errors.append(f'at least {PASSWORD_MIN_LENGTH} characters')
    if not re.search(r'[A-Z]', password):
        errors.append('an uppercase letter')
    if not re.search(r'[a-z]', password):
        errors.append('a lowercase letter')
    if not re.search(r'\d', password):
        errors.append('a digit')
    if errors:
        raise RestAPIException(
            status_code=StatusCode.HTTP_400_BAD_REQUEST,
            error_code='password_too_weak',
            message=f'Password must contain: {", ".join(errors)}',
        )


class ChangePasswordInputSchema(Schema):
    old_password: str = ''
    new_password: str


class ChangePasswordOutputSchema(Schema):
    is_success: bool
    msg: str


class ChangePasswordView(SimplePostAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return ChangePasswordOutputSchema

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return ChangePasswordInputSchema

    @classmethod
    async def check_permitted(cls, request: APIRequest, data: ChangePasswordInputSchema, path: Path = None) -> None:
        user_obj = await request.future_user
        await LoginPermissionChecker().async_raise_exception_if_not_valid(user_obj)

    @classmethod
    async def run_action(cls, request: APIRequest, data: ChangePasswordInputSchema, path: Path = None
                         ) -> ChangePasswordOutputSchema:
        user_obj: User = await request.future_user

        await LoginPermissionChecker().async_raise_exception_if_not_valid(user_obj)

        validate_new_password(str(data.new_password))

        if user_obj.password and user_obj.has_usable_password():
            old_pass = str(data.old_password)
            user = await DjangoAuth.async_authenticate(username=user_obj.username, password=old_pass)
            if not user:
                raise RestAPIException(
                    status_code=StatusCode.HTTP_401_UNAUTHORIZED,
                    error_code='password_is_incorrect',
                    message='Old password is incorrect',
                )
            user_obj = user

        user_obj.set_password(str(data.new_password))
        await user_obj.asave()
        return ChangePasswordOutputSchema(is_success=True, msg='Password successfully changed')
