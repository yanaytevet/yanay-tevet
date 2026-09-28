from typing import Type

from ninja import Path, Query, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.views.item_by_id_api_mixin import ItemByIdPath
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from special_dates.managers.special_date_calendar_manager import SpecialDateCalendarManager
from special_dates.models.special_date_calendar import SpecialDateCalendar
from special_dates.permissions_checkers.special_date_calendar_member_permission_checker import (
    SpecialDateCalendarMemberPermissionChecker,
)
from special_dates.serializers.special_date_calendar_serializers.special_date_calendar_member_serializer import (
    SpecialDateCalendarMemberSchema,
    SpecialDateCalendarMemberSerializer,
)
from users.serializers.invitation.pending_invitation_serializer import (
    PendingInvitationSchema,
    PendingInvitationSerializer,
)


class SpecialDateCalendarMembersSchema(Schema):
    members: list[SpecialDateCalendarMemberSchema]
    pending_invitations: list[PendingInvitationSchema]


class ListSpecialDateCalendarMembersView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return SpecialDateCalendarMembersSchema

    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return ItemByIdPath

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> SpecialDateCalendarMembersSchema:
        calendar = await SpecialDateCalendar.objects.filter(id=path.object_id).afirst()
        if calendar is None:
            raise ObjectDoesntExistAPIException(SpecialDateCalendar, path.object_id)
        user = await api_request.future_user
        await SpecialDateCalendarMemberPermissionChecker(calendar).async_raise_exception_if_not_valid(user)
        manager = SpecialDateCalendarManager(user)
        member_serializer = SpecialDateCalendarMemberSerializer(user)
        pending_serializer = PendingInvitationSerializer()
        return SpecialDateCalendarMembersSchema(
            members=[await member_serializer.serialize(m) for m in await manager.list_members(calendar)],
            pending_invitations=[await pending_serializer.serialize(p) for p in await manager.list_pending_invitations(calendar)],
        )
