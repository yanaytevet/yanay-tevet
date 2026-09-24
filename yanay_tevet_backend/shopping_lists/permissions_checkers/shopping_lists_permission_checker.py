from users.enums.permissions import Permissions
from users.permissions_checkers.has_permission_checker import HasPermissionChecker


class ShoppingListsPermissionChecker(HasPermissionChecker):
    def __init__(self) -> None:
        super().__init__(Permissions.SHOPPING_LISTS)
