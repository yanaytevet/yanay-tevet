from typing import Type

from ninja import Path, Schema
from pydantic import Field

from common.simple_api.api_request import APIRequest
from special_dates.managers.special_date_calendar_manager import SpecialDateCalendarManager
from special_dates.models.special_date_calendar import SpecialDateCalendar
from special_dates.views.calendar_views.special_date_calendar_action_view import SpecialDateCalendarActionView


class RenameSpecialDateCalendarSchema(Schema):
    name: str = Field(min_length=1, max_length=100)


class RenameSpecialDateCalendarView(SpecialDateCalendarActionView):
    requires_owner = True

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return RenameSpecialDateCalendarSchema

    @classmethod
    async def run_action(cls, request: APIRequest, obj: SpecialDateCalendar, data: RenameSpecialDateCalendarSchema, path: Path) -> None:
        await SpecialDateCalendarManager(await request.future_user).rename(obj, data.name)
        return None
