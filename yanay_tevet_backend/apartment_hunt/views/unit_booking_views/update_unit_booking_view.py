from datetime import date
from typing import Optional, Type

from django.db.models import Model
from ninja import Path, Schema

from apartment_hunt.managers.unit_booking_manager import UnitBookingManager
from apartment_hunt.models.unit_booking import UnitBooking
from apartment_hunt.permissions_checkers.booking_permission_checker import BookingPermissionChecker
from apartment_hunt.serializers.unit_booking_serializers.unit_booking_serializer import UnitBookingSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.update_views.update_item_by_id_api_view import UpdateItemByIdAPIView


class UpdateUnitBookingSchema(Schema):
    note: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class UpdateUnitBookingView(UpdateItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return UpdateUnitBookingSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return UnitBookingSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return UnitBooking

    @classmethod
    async def serialize_object(cls, request: APIRequest, obj: UnitBooking) -> Schema:
        # Only the creator or a project owner/admin can reach this view, so names are visible to them.
        user = await request.future_user
        return await UnitBookingSerializer(user, can_see_all_names=True).serialize(obj)

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: UnitBooking, data: Schema, path: Path) -> None:
        unit = await obj.get_unit()
        project = await unit.get_project()
        await BookingPermissionChecker(obj, project).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def update_object(cls, request: APIRequest, obj: UnitBooking, data: UpdateUnitBookingSchema, path: Path) -> None:
        user = await request.future_user
        await UnitBookingManager(user).update_booking(obj, data.note, data.start_date, data.end_date)
