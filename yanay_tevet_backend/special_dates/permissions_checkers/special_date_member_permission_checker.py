from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.permissions_checkers.permissions_checker import PermissionsChecker
from special_dates.models.special_date import SpecialDate
from special_dates.models.special_date_calendar_membership import SpecialDateCalendarMembership
from users.models import User


class SpecialDateMemberPermissionChecker(PermissionsChecker):
    """Any member of the event's calendar may view and edit it."""

    def __init__(self, special_date: SpecialDate) -> None:
        self.special_date = special_date

    async def async_raise_exception_if_not_valid(self, user: User | None) -> None:
        if self.special_date.calendar_id is None:
            allowed = self.special_date.created_by_id == user.id
        else:
            allowed = await SpecialDateCalendarMembership.objects.filter(
                calendar_id=self.special_date.calendar_id, user_id=user.id
            ).aexists()
        if not allowed:
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='האירוע הזה לא שייך ללוח שלך.',
                error_code='not_calendar_member',
            )
