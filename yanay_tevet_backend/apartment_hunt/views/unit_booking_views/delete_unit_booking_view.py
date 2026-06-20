from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from apartment_hunt.models.unit_booking import UnitBooking
from apartment_hunt.permissions_checkers.booking_permission_checker import BookingPermissionChecker
from common.simple_api.api_request import APIRequest
from common.simple_api.views.delete_views.delete_item_by_id_api_view import DeleteItemByIdAPIView


class DeleteUnitBookingView(DeleteItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return UnitBooking

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: UnitBooking, data: Schema, path: Path) -> None:
        unit = await obj.get_unit()
        project = await unit.get_project()
        await BookingPermissionChecker(obj, project).async_raise_exception_if_not_valid(
            await request.future_user
        )
