from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.permissions_checkers.permissions_checker import PermissionsChecker
from special_dates.enums.special_date_calendar_role import SpecialDateCalendarRole
from special_dates.models.special_date_calendar import SpecialDateCalendar
from special_dates.models.special_date_calendar_membership import SpecialDateCalendarMembership
from users.models import User


class SpecialDateCalendarMemberPermissionChecker(PermissionsChecker):
    def __init__(self, calendar: SpecialDateCalendar, require_owner: bool = False) -> None:
        self.calendar = calendar
        self.require_owner = require_owner

    async def async_raise_exception_if_not_valid(self, user: User | None) -> None:
        membership = await SpecialDateCalendarMembership.objects.filter(
            calendar_id=self.calendar.id, user_id=user.id
        ).afirst()
        if membership is None:
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='אינך חבר/ה בלוח הזה.',
                error_code='not_calendar_member',
            )
        if self.require_owner and membership.role != SpecialDateCalendarRole.OWNER:
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='רק הבעלים של הלוח יכול/ה לעשות את זה.',
                error_code='not_calendar_owner',
            )
