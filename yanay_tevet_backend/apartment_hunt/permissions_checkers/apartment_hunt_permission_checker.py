from users.enums.permissions import Permissions
from users.models import User
from users.permissions_checkers.has_permission_checker import HasPermissionChecker


class ApartmentHuntPermissionChecker(HasPermissionChecker):
    def __init__(self) -> None:
        super().__init__(Permissions.APARTMENT_HUNT)

    async def async_raise_exception_if_not_valid(self, user: User | None) -> None:
        await super().async_raise_exception_if_not_valid(user)
