from datetime import date
from typing import Optional, Type

from django.db.models import Model, QuerySet
from ninja import Field, FilterSchema, Path, Query, Schema

from apartment_hunt.models.unit import Unit
from apartment_hunt.models.unit_booking import UnitBooking
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from apartment_hunt.serializers.unit_booking_serializers.unit_booking_serializer import UnitBookingSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.pagination.paginate_items_api_view import PaginateItemsAPIView


class UnitBookingsByUnitPath(Schema):
    unit_id: int


class PaginateUnitBookingsFilterSchema(FilterSchema):
    # Keep only bookings overlapping the requested [from_date, to_date) window.
    to_date: Optional[date] = Field(default=None, q='start_date__lt')
    from_date: Optional[date] = Field(default=None, q='end_date__gt')


class PaginateUnitBookingsView(PaginateItemsAPIView):
    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return UnitBookingsByUnitPath

    @classmethod
    async def check_permitted_before_pagination(cls, request: APIRequest, query: Query, path: Path) -> None:
        unit = await Unit.objects.filter(id=path.unit_id).afirst()
        if unit is None:
            raise ObjectDoesntExistAPIException(Unit, path.unit_id)
        project = await unit.get_project()
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(
            await request.future_user
        )

    @classmethod
    def get_serializer(cls) -> Serializer:
        return UnitBookingSerializer()

    @classmethod
    def get_allowed_order_by(cls) -> set[str]:
        return {'id', 'start_date', 'end_date', 'created_at'}

    @classmethod
    def get_filter_schema(cls) -> Type[FilterSchema]:
        return PaginateUnitBookingsFilterSchema

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return UnitBooking

    @classmethod
    async def apply_initial_filter_and_order(cls, queryset: QuerySet, request: APIRequest,
                                             query: Query, path: Path) -> QuerySet:
        return queryset.filter(unit_id=path.unit_id).order_by('start_date', 'id')
