from typing import Type

from ninja import Schema, Path

from common.simple_api.api_request import APIRequest
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.permissions_checkers.not_logged_in_permission_checker import NotLoggedInPermissionChecker
from common.simple_api.schemas.empty_schema import EmptySchema
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from users.models import User, TemporaryAccess


class ForgotMyPasswordSchema(Schema):
    email: str


class ForgotMyPasswordView(SimplePostAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return EmptySchema

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return ForgotMyPasswordSchema

    @classmethod
    async def check_permitted(cls, request: APIRequest, data: ForgotMyPasswordSchema, path: Path = None) -> None:
        await NotLoggedInPermissionChecker().async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def run_action(cls, request: APIRequest, data: ForgotMyPasswordSchema, path: Path = None) -> EmptySchema:
        user_obj = await User.async_get_by_username(data.email.lower().replace(' ', ''))
        if not user_obj:
            raise RestAPIException(
                status_code=StatusCode.HTTP_401_UNAUTHORIZED,
                error_code='incorrect_user',
                message='Incorrect user',
            )

        if TemporaryAccess.user_id_already_has(user_obj.id):
            message = f'''Email was already sent in the last {TemporaryAccess.TTL_MINUTES} minutes.
            If it wasn't you or the email didn\'t arrive, please contact our customers  support.'''
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                error_code='email_was_already_sent',
                message=message,
            )

        temporary_access = TemporaryAccess.create_for_user(user_obj)
        # send_forgot_my_password_emails_task.delay(temporary_access.id)
        return EmptySchema()
