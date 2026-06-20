from typing import Type

from ninja import Path, Query, Schema

from apartment_hunt.managers.unit_booking_manager import UnitBookingManager
from apartment_hunt.models.unit import Unit
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from apartment_hunt.serializers.unit_booking_serializers.unit_booking_serializer import (
    UnitBookingSchema,
    UnitBookingSerializer,
)
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView


class UnitCalendarPath(Schema):
    unit_id: int


class UnitCalendarSchema(Schema):
    bookings: list[UnitBookingSchema]
    can_manage_all: bool


class GetUnitCalendarView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return UnitCalendarSchema

    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return UnitCalendarPath

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> UnitCalendarSchema:
        unit = await Unit.objects.filter(id=path.unit_id).afirst()
        if unit is None:
            raise ObjectDoesntExistAPIException(Unit, path.unit_id)
        project = await unit.get_project()
        user = await api_request.future_user
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(user)
        manager = UnitBookingManager(user)
        can_manage_all = await manager.can_manage_all(project)
        serializer = UnitBookingSerializer(user, can_see_all_names=can_manage_all)
        bookings = [
            await serializer.serialize(b)
            async for b in unit.bookings.order_by('start_date', 'id')
        ]
        return UnitCalendarSchema(bookings=bookings, can_manage_all=can_manage_all)
