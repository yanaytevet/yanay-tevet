from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.permissions_checkers.permissions_checker import PermissionsChecker
from special_dates.models.special_date import SpecialDate
from users.models import User


class OwnSpecialDatePermissionChecker(PermissionsChecker):
    def __init__(self, special_date: SpecialDate) -> None:
        self.special_date = special_date

    async def async_raise_exception_if_not_valid(self, user: User | None) -> None:
        if self.special_date.owner_id != user.id:
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='This event does not belong to you.',
                error_code='not_owner',
            )
