from typing import Type

from ninja import Path, Query, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from special_dates.managers.special_date_calendar_manager import SpecialDateCalendarManager
from special_dates.serializers.special_date_calendar_serializers.special_date_calendar_serializer import (
    SpecialDateCalendarSchema,
    SpecialDateCalendarSerializer,
)


class SpecialDateCalendarsSchema(Schema):
    calendars: list[SpecialDateCalendarSchema]


class ListSpecialDateCalendarsView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return SpecialDateCalendarsSchema

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> SpecialDateCalendarsSchema:
        user = await api_request.future_user
        manager = SpecialDateCalendarManager(user)
        await manager.ensure_personal_calendar()
        serializer = SpecialDateCalendarSerializer(user)
        return SpecialDateCalendarsSchema(
            calendars=[await serializer.serialize(c.calendar) for c in await manager.list_for_user()],
        )
