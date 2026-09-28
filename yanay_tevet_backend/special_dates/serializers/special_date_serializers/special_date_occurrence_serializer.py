from datetime import date

from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from special_dates.enums.calendar_type import CalendarType
from special_dates.managers.special_date_manager import SpecialDateManager, SpecialDateOccurrence
from special_dates.serializers.special_date_serializers.special_date_serializer import (
    SpecialDateSchema,
    SpecialDateSerializer,
)


class SpecialDateOccurrenceSchema(Schema):
    special_date: SpecialDateSchema
    date: date
    hebrew_date: str
    calendars: list[CalendarType]
    years: int
    days_until: int


class SpecialDateOccurrenceSerializer(Serializer[SpecialDateOccurrenceSchema]):
    async def inner_serialize(self, obj: SpecialDateOccurrence) -> SpecialDateOccurrenceSchema:
        return SpecialDateOccurrenceSchema(
            special_date=await SpecialDateSerializer().serialize(obj.special_date),
            date=obj.date,
            hebrew_date=SpecialDateManager.format_hebrew_date(obj.date, False),
            calendars=obj.calendars,
            years=obj.years,
            days_until=obj.days_until,
        )
