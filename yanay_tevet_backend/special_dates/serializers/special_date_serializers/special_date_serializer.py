from datetime import date, datetime

from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from special_dates.enums.special_date_category import SpecialDateCategory
from special_dates.enums.special_date_recurrence import SpecialDateRecurrence
from special_dates.managers.special_date_manager import SpecialDateManager
from special_dates.models.special_date import SpecialDate


class SpecialDateSchema(Schema):
    id: int
    date: date
    after_sunset: bool
    category: SpecialDateCategory
    recurrence: SpecialDateRecurrence
    description: str
    hebrew_date: str
    next_gregorian_date: date
    next_hebrew_date: date
    created_at: datetime
    updated_at: datetime


class SpecialDateSerializer(Serializer[SpecialDateSchema]):
    async def inner_serialize(self, obj: SpecialDate) -> SpecialDateSchema:
        today = SpecialDateManager.today()
        next_gregorian_date, _ = SpecialDateManager.next_gregorian_occurrence(obj, today)
        next_hebrew_date, _ = SpecialDateManager.next_hebrew_occurrence(obj, today)
        return SpecialDateSchema(
            id=obj.id,
            date=obj.date,
            after_sunset=obj.after_sunset,
            category=SpecialDateCategory(obj.category),
            recurrence=SpecialDateRecurrence(obj.recurrence),
            description=obj.description,
            hebrew_date=SpecialDateManager.format_hebrew_date(obj.date, obj.after_sunset),
            next_gregorian_date=next_gregorian_date,
            next_hebrew_date=next_hebrew_date,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
