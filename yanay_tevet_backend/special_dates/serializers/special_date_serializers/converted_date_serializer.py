from datetime import date

from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from special_dates.managers.special_date_manager import ConvertedDate
from special_dates.utils.hebrew_calendar import HebrewCalendar


class ConvertedDateSchema(Schema):
    date: date
    after_sunset: bool
    hebrew_year: int
    hebrew_month: int
    hebrew_day: int
    hebrew_date: str


class ConvertedDateSerializer(Serializer[ConvertedDateSchema]):
    async def inner_serialize(self, obj: ConvertedDate) -> ConvertedDateSchema:
        return ConvertedDateSchema(
            date=obj.date,
            after_sunset=obj.after_sunset,
            hebrew_year=obj.hebrew.year,
            hebrew_month=obj.hebrew.month,
            hebrew_day=obj.hebrew.day,
            hebrew_date=HebrewCalendar.format(obj.hebrew),
        )
