from django.contrib.auth.models import User

from ..enums.status_code import StatusCode
from ..exceptions.rest_api_exception import RestAPIException
from .permissions_checker import PermissionsChecker


must_not_be_logged_in_api_exception = RestAPIException(
    status_code=StatusCode.HTTP_403_FORBIDDEN,
    message='Must not be logged in.',
    error_code='must_not_be_logged_in',
)


class NotLoggedInPermissionChecker(PermissionsChecker):
    async def async_raise_exception_if_not_valid(self, user: User) -> None:
        if user and not user.is_anonymous:
            raise must_not_be_logged_in_api_exception
