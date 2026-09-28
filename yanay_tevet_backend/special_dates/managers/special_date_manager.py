from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from special_dates.enums.calendar_type import CalendarType
from special_dates.enums.special_date_recurrence import SpecialDateRecurrence
from special_dates.models.special_date import SpecialDate
from special_dates.utils.hebrew_calendar import HebrewCalendar, HebrewDate
from users.models import User

MAX_SPECIAL_DATES_PER_USER = 500
UPCOMING_DAYS = 14
LOCAL_TIMEZONE = ZoneInfo('Asia/Jerusalem')


@dataclass
class SpecialDateOccurrence:
    special_date: SpecialDate
    date: date
    calendars: list[CalendarType]
    years: int
    days_until: int


class SpecialDateManager:
    def __init__(self, user: User | None = None) -> None:
        self.user = user

    @staticmethod
    def today() -> date:
        return datetime.now(LOCAL_TIMEZONE).date()

    @staticmethod
    def hebrew_date_of(gregorian: date, after_sunset: bool) -> HebrewDate:
        """The Hebrew day starts at sunset, so an event after sunset belongs to the next Hebrew day."""
        ordinal = gregorian.toordinal() + (1 if after_sunset else 0)
        return HebrewCalendar.from_ordinal(ordinal)

    @staticmethod
    def format_hebrew_date(gregorian: date, after_sunset: bool) -> str:
        return HebrewCalendar.format(SpecialDateManager.hebrew_date_of(gregorian, after_sunset))

    @staticmethod
    def _gregorian_in_year(original: date, year: int) -> date:
        if original.month == 2 and original.day == 29:
            try:
                return date(year, 2, 29)
            except ValueError:
                return date(year, 2, 28)
        return original.replace(year=year)

    @staticmethod
    def next_gregorian_occurrence(special_date: SpecialDate, from_date: date) -> tuple[date, int]:
        year = max(from_date.year, special_date.date.year)
        occurrence = SpecialDateManager._gregorian_in_year(special_date.date, year)
        if occurrence < from_date:
            year += 1
            occurrence = SpecialDateManager._gregorian_in_year(special_date.date, year)
        return occurrence, year - special_date.date.year

    @staticmethod
    def next_hebrew_occurrence(special_date: SpecialDate, from_date: date) -> tuple[date, int]:
        original = SpecialDateManager.hebrew_date_of(special_date.date, special_date.after_sunset)
        year = max(HebrewCalendar.from_gregorian(from_date).year, original.year)
        occurrence = HebrewCalendar.to_gregorian(HebrewCalendar.anniversary_in_year(original, year))
        if occurrence < from_date:
            year += 1
            occurrence = HebrewCalendar.to_gregorian(HebrewCalendar.anniversary_in_year(original, year))
        return occurrence, year - original.year

    def occurrences_between(self, special_date: SpecialDate, from_date: date, to_date: date) -> list[SpecialDateOccurrence]:
        candidates: list[tuple[date, int, CalendarType]] = []
        if special_date.recurrence != SpecialDateRecurrence.HEBREW:
            occurrence, years = self.next_gregorian_occurrence(special_date, from_date)
            candidates.append((occurrence, years, CalendarType.GREGORIAN))
        if special_date.recurrence != SpecialDateRecurrence.GREGORIAN:
            occurrence, years = self.next_hebrew_occurrence(special_date, from_date)
            candidates.append((occurrence, years, CalendarType.HEBREW))

        by_date: dict[date, SpecialDateOccurrence] = {}
        for occurrence, years, calendar in candidates:
            if occurrence > to_date:
                continue
            existing = by_date.get(occurrence)
            if existing is not None:
                existing.calendars.append(calendar)
                continue
            by_date[occurrence] = SpecialDateOccurrence(
                special_date=special_date,
                date=occurrence,
                calendars=[calendar],
                years=years,
                days_until=(occurrence - from_date).days,
            )
        return list(by_date.values())

    async def upcoming(self, days: int = UPCOMING_DAYS) -> list[SpecialDateOccurrence]:
        from_date = self.today()
        to_date = from_date + timedelta(days=days)
        occurrences: list[SpecialDateOccurrence] = []
        async for special_date in SpecialDate.objects.filter(owner_id=self.user.id):
            occurrences.extend(self.occurrences_between(special_date, from_date, to_date))
        occurrences.sort(key=lambda o: (o.date, o.special_date.description))
        return occurrences

    async def count(self) -> int:
        return await SpecialDate.objects.filter(owner_id=self.user.id).acount()

    async def raise_if_limit_reached(self) -> None:
        if await self.count() >= MAX_SPECIAL_DATES_PER_USER:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message=f'הגעת למגבלה של {MAX_SPECIAL_DATES_PER_USER} אירועים.',
                error_code='special_dates_limit_reached',
            )
