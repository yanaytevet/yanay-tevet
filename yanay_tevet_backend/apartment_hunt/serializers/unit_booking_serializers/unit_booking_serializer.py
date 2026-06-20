from datetime import date, datetime
from typing import Optional

from ninja import Schema

from apartment_hunt.models.unit_booking import UnitBooking
from common.simple_api.serializers.serializer import Serializer
from users.models import User


class UnitBookingSchema(Schema):
    id: int
    unit_id: int
    start_date: date
    end_date: date
    note: str
    created_by_id: Optional[int]
    created_by_name: str
    created_at: datetime


class UnitBookingSerializer(Serializer[UnitBookingSchema]):
    def __init__(self, user: User | None = None, can_see_all_names: bool = False) -> None:
        super().__init__(user)
        self.can_see_all_names = can_see_all_names

    async def inner_serialize(self, obj: UnitBooking) -> UnitBookingSchema:
        is_own = self.user is not None and obj.created_by_id == self.user.id
        show_name = self.can_see_all_names or is_own
        creator: Optional[User] = None
        if show_name and obj.created_by_id is not None:
            creator = await User.objects.filter(id=obj.created_by_id).afirst()
        return UnitBookingSchema(
            id=obj.id,
            unit_id=obj.unit_id,
            start_date=obj.start_date,
            end_date=obj.end_date,
            note=obj.note if show_name else '',
            created_by_id=obj.created_by_id,
            created_by_name=creator.get_full_name() if creator else '',
            created_at=obj.created_at,
        )
