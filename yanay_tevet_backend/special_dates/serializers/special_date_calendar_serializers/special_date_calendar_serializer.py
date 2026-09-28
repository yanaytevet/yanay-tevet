from typing import Optional

from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from special_dates.enums.special_date_calendar_role import SpecialDateCalendarRole
from special_dates.managers.special_date_manager import MAX_SPECIAL_DATES_PER_CALENDAR, SpecialDateManager
from special_dates.models.special_date_calendar import SpecialDateCalendar
from special_dates.models.special_date_calendar_membership import SpecialDateCalendarMembership


class SpecialDateCalendarSchema(Schema):
    id: int
    name: str
    owner_name: str
    is_owner: bool
    member_count: int
    event_count: int
    max_event_count: int
    hide_from_upcoming: bool
    join_token: Optional[str]


class SpecialDateCalendarSerializer(Serializer[SpecialDateCalendarSchema]):
    """Serialized from the point of view of `self.user` — only the owner sees the join token."""

    async def inner_serialize(self, obj: SpecialDateCalendar) -> SpecialDateCalendarSchema:
        membership = await SpecialDateCalendarMembership.objects.filter(calendar_id=obj.id, user_id=self.user.id).afirst()
        is_owner = membership is not None and membership.role == SpecialDateCalendarRole.OWNER
        return SpecialDateCalendarSchema(
            id=obj.id,
            name=obj.name,
            owner_name=SpecialDateManager.display_name(await obj.get_owner()),
            is_owner=is_owner,
            member_count=await obj.memberships.acount(),
            event_count=await SpecialDateManager.count_in_calendar(obj),
            max_event_count=MAX_SPECIAL_DATES_PER_CALENDAR,
            hide_from_upcoming=membership.hide_from_upcoming if membership is not None else False,
            join_token=obj.join_token if is_owner else None,
        )
