from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.permissions_checkers.login_permission_checker import LoginPermissionChecker
from common.simple_api.permissions_checkers.permissions_checker import PermissionsChecker
from users.enums.permissions import Permissions
from users.models import User


class HasPermissionChecker(PermissionsChecker):
    def __init__(self, permission: Permissions):
        self.permission = permission

    async def async_raise_exception_if_not_valid(self, user: User | None) -> None:
        await LoginPermissionChecker().async_raise_exception_if_not_valid(user)
        if not user.is_admin() and self.permission not in user.permissions:
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='User does not have the required permission.',
                error_code='missing_permission',
            )
