from datetime import date
from typing import Type

from ninja import Path, Query, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from special_dates.managers.special_date_manager import (
    MAX_SPECIAL_DATES_PER_USER,
    UPCOMING_DAYS,
    SpecialDateManager,
)
from special_dates.serializers.special_date_serializers.special_date_occurrence_serializer import (
    SpecialDateOccurrenceSchema,
    SpecialDateOccurrenceSerializer,
)


class UpcomingSpecialDatesSchema(Schema):
    today: date
    today_hebrew_date: str
    days: int
    occurrences: list[SpecialDateOccurrenceSchema]
    total_count: int
    max_count: int


class GetUpcomingSpecialDatesView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return UpcomingSpecialDatesSchema

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> UpcomingSpecialDatesSchema:
        manager = SpecialDateManager(await api_request.future_user)
        today = manager.today()
        serializer = SpecialDateOccurrenceSerializer()
        occurrences = [await serializer.serialize(o) for o in await manager.upcoming(UPCOMING_DAYS)]
        return UpcomingSpecialDatesSchema(
            today=today,
            today_hebrew_date=manager.format_hebrew_date(today, False),
            days=UPCOMING_DAYS,
            occurrences=occurrences,
            total_count=await manager.count(),
            max_count=MAX_SPECIAL_DATES_PER_USER,
        )
