from typing import Type

from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from special_dates.managers.special_date_calendar_manager import SpecialDateCalendarManager
from special_dates.models.special_date_calendar import SpecialDateCalendar
from special_dates.views.calendar_views.special_date_calendar_action_view import SpecialDateCalendarActionView


class RemoveSpecialDateCalendarMemberSchema(Schema):
    user_id: int


class RemoveSpecialDateCalendarMemberView(SpecialDateCalendarActionView):
    requires_owner = True

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return RemoveSpecialDateCalendarMemberSchema

    @classmethod
    async def run_action(cls, request: APIRequest, obj: SpecialDateCalendar, data: RemoveSpecialDateCalendarMemberSchema, path: Path) -> None:
        await SpecialDateCalendarManager(await request.future_user).remove_member(obj, data.user_id)
        return None
