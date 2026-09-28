from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from special_dates.managers.special_date_manager import SpecialDateManager
from special_dates.models.special_date_calendar import SpecialDateCalendar


class SpecialDateCalendarJoinPreviewSchema(Schema):
    calendar_name: str
    owner_name: str
    member_count: int
    event_count: int


class SpecialDateCalendarJoinPreviewSerializer(Serializer[SpecialDateCalendarJoinPreviewSchema]):
    """What a (possibly logged-out) visitor sees before joining — no event contents, no member names."""

    async def inner_serialize(self, obj: SpecialDateCalendar) -> SpecialDateCalendarJoinPreviewSchema:
        return SpecialDateCalendarJoinPreviewSchema(
            calendar_name=obj.name,
            owner_name=SpecialDateManager.display_name(await obj.get_owner()),
            member_count=await obj.memberships.acount(),
            event_count=await SpecialDateManager.count_in_calendar(obj),
        )
