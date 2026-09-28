from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from special_dates.enums.special_date_calendar_role import SpecialDateCalendarRole
from special_dates.managers.special_date_manager import SpecialDateManager
from special_dates.models.special_date_calendar_membership import SpecialDateCalendarMembership


class SpecialDateCalendarMemberSchema(Schema):
    user_id: int
    name: str
    email: str
    role: SpecialDateCalendarRole
    is_me: bool


class SpecialDateCalendarMemberSerializer(Serializer[SpecialDateCalendarMemberSchema]):
    async def inner_serialize(self, obj: SpecialDateCalendarMembership) -> SpecialDateCalendarMemberSchema:
        user = await obj.get_user()
        return SpecialDateCalendarMemberSchema(
            user_id=obj.user_id,
            name=SpecialDateManager.display_name(user),
            email=user.email if user is not None else '',
            role=SpecialDateCalendarRole(obj.role),
            is_me=self.user is not None and obj.user_id == self.user.id,
        )
