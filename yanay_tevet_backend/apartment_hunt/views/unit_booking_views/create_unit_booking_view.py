from datetime import date
from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from apartment_hunt.managers.unit_booking_manager import UnitBookingManager
from apartment_hunt.models.unit import Unit
from apartment_hunt.models.unit_booking import UnitBooking
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from apartment_hunt.serializers.unit_booking_serializers.unit_booking_serializer import UnitBookingSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView


class CreateUnitBookingSchema(Schema):
    unit_id: int
    start_date: date
    end_date: date
    note: str = ''


class CreateUnitBookingView(CreateItemAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreateUnitBookingSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return UnitBookingSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return UnitBooking

    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: CreateUnitBookingSchema, path: Path) -> None:
        unit = await Unit.objects.filter(id=data.unit_id).afirst()
        if unit is None:
            raise ObjectDoesntExistAPIException(Unit, data.unit_id)
        project = await unit.get_project()
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(
            await request.future_user
        )

    @classmethod
    async def create_object(cls, request: APIRequest, data: CreateUnitBookingSchema, path: Path) -> Model:
        user = await request.future_user
        return await UnitBookingManager(user).create_booking(
            data.unit_id, data.start_date, data.end_date, data.note
        )
