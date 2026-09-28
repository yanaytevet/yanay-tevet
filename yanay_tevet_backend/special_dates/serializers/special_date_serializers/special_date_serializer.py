from datetime import date, datetime
from typing import Optional

from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from special_dates.enums.calendar_type import CalendarType
from special_dates.enums.special_date_category import SpecialDateCategory
from special_dates.managers.special_date_manager import SpecialDateManager
from special_dates.models.special_date import SpecialDate
from special_dates.utils.hebrew_calendar import HebrewCalendar


class SpecialDateSchema(Schema):
    id: int
    name: str
    category: SpecialDateCategory
    date: date
    after_sunset: bool
    input_calendar: CalendarType
    hebrew_year: int
    hebrew_month: int
    hebrew_day: int
    hebrew_date: str
    remind_hebrew: bool
    remind_gregorian: bool
    next_gregorian_date: Optional[date]
    next_hebrew_date: Optional[date]
    created_at: datetime
    updated_at: datetime


class SpecialDateSerializer(Serializer[SpecialDateSchema]):
    async def inner_serialize(self, obj: SpecialDate) -> SpecialDateSchema:
        today = SpecialDateManager.today()
        hebrew = SpecialDateManager.hebrew_date_of(obj.date, obj.after_sunset)
        next_gregorian_date = None
        if obj.remind_gregorian:
            next_gregorian_date, _ = SpecialDateManager.next_gregorian_occurrence(obj, today)
        next_hebrew_date = None
        if obj.remind_hebrew:
            next_hebrew_date, _ = SpecialDateManager.next_hebrew_occurrence(obj, today)
        return SpecialDateSchema(
            id=obj.id,
            name=obj.name,
            category=SpecialDateCategory(obj.category),
            date=obj.date,
            after_sunset=obj.after_sunset,
            input_calendar=CalendarType(obj.input_calendar),
            hebrew_year=hebrew.year,
            hebrew_month=hebrew.month,
            hebrew_day=hebrew.day,
            hebrew_date=HebrewCalendar.format(hebrew),
            remind_hebrew=obj.remind_hebrew,
            remind_gregorian=obj.remind_gregorian,
            next_gregorian_date=next_gregorian_date,
            next_hebrew_date=next_hebrew_date,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
