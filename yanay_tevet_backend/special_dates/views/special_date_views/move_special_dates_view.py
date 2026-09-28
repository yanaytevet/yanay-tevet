from typing import Type

from ninja import Path, Schema
from pydantic import Field

from common.simple_api.api_request import APIRequest
from common.simple_api.schemas.empty_schema import EmptySchema
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from special_dates.managers.special_date_calendar_manager import SpecialDateCalendarManager
from special_dates.managers.special_date_manager import MAX_SPECIAL_DATES_PER_CALENDAR, SpecialDateManager
from special_dates.models.special_date import SpecialDate
from special_dates.permissions_checkers.special_date_member_permission_checker import SpecialDateMemberPermissionChecker


class MoveSpecialDatesSchema(Schema):
    special_date_ids: list[int] = Field(min_length=1, max_length=MAX_SPECIAL_DATES_PER_CALENDAR)
    calendar_id: int


class MoveSpecialDatesView(SimplePostAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return EmptySchema

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return MoveSpecialDatesSchema

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, data: Schema = None, path: Path = None) -> None:
        pass

    @classmethod
    async def run_action(cls, api_request: APIRequest, data: MoveSpecialDatesSchema, path: Path = None) -> EmptySchema:
        user = await api_request.future_user
        target = await SpecialDateCalendarManager(user).get_member_calendar(data.calendar_id)
        special_dates = [d async for d in SpecialDate.objects.filter(id__in=data.special_date_ids)]
        for special_date in special_dates:
            await SpecialDateMemberPermissionChecker(special_date).async_raise_exception_if_not_valid(user)
        await SpecialDateManager(user).move(special_dates, target)
        return EmptySchema()
