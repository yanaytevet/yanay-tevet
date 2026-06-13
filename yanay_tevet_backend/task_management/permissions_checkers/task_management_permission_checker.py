from users.enums.permissions import Permissions
from users.models import User
from users.permissions_checkers.has_permission_checker import HasPermissionChecker


class TaskManagementPermissionChecker(HasPermissionChecker):
    def __init__(self) -> None:
        super().__init__(Permissions.TASK_MANAGEMENT)

    async def async_raise_exception_if_not_valid(self, user: User | None) -> None:
        await super().async_raise_exception_if_not_valid(user)
