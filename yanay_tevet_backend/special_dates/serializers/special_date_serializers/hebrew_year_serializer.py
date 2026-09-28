from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from special_dates.managers.special_date_manager import SpecialDateManager
from special_dates.utils.hebrew_calendar import HebrewCalendar


class HebrewOptionSchema(Schema):
    value: int
    label: str


class HebrewMonthOptionSchema(Schema):
    value: int
    label: str
    days: int


class HebrewYearSchema(Schema):
    year: int
    is_leap: bool
    months: list[HebrewMonthOptionSchema]
    days: list[HebrewOptionSchema]
    years: list[HebrewOptionSchema]


class HebrewYearSerializer(Serializer[HebrewYearSchema]):
    """Everything the Hebrew date picker needs for one year: its months (with lengths), day and year labels."""

    async def inner_serialize(self, obj: int) -> HebrewYearSchema:
        year = obj
        return HebrewYearSchema(
            year=year,
            is_leap=HebrewCalendar.is_leap_year(year),
            months=[
                HebrewMonthOptionSchema(
                    value=month,
                    label=HebrewCalendar.month_name(year, month),
                    days=HebrewCalendar.days_in_month(year, month),
                )
                for month in HebrewCalendar.months_in_year_order(year)
            ],
            days=[HebrewOptionSchema(value=day, label=HebrewCalendar.gematria(day)) for day in range(1, 31)],
            years=[
                HebrewOptionSchema(value=y, label=f'{HebrewCalendar.gematria(y)} ({y})')
                for y in SpecialDateManager.selectable_hebrew_years()
            ],
        )
