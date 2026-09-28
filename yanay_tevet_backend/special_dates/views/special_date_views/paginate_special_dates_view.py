from typing import Optional, Type

from django.db.models import Model, QuerySet
from ninja import FilterSchema, Path, Query
from pydantic import Field

from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.pagination.paginate_items_api_view import PaginateItemsAPIView
from special_dates.enums.special_date_category import SpecialDateCategory
from special_dates.managers.special_date_calendar_manager import SpecialDateCalendarManager
from special_dates.models.special_date import SpecialDate
from special_dates.serializers.special_date_serializers.special_date_serializer import SpecialDateSerializer


class PaginateSpecialDatesFilterSchema(FilterSchema):
    search: Optional[str] = Field(None, q=['name__icontains'])
    category: Optional[SpecialDateCategory] = None
    calendar_id: Optional[int] = None


class PaginateSpecialDatesView(PaginateItemsAPIView):
    @classmethod
    async def check_permitted_before_pagination(cls, request: APIRequest, query: Query, path: Path) -> None:
        pass

    @classmethod
    def get_serializer(cls) -> Serializer:
        return SpecialDateSerializer()

    @classmethod
    def get_allowed_order_by(cls) -> set[str]:
        return {'id', 'date', 'name', 'category', 'created_at'}

    @classmethod
    def get_filter_schema(cls) -> Type[FilterSchema]:
        return PaginateSpecialDatesFilterSchema

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return SpecialDate

    @classmethod
    async def apply_initial_filter_and_order(cls, queryset: QuerySet, request: APIRequest,
                                             query: Query, path: Path) -> QuerySet:
        manager = SpecialDateCalendarManager(await request.future_user)
        await manager.ensure_personal_calendar()
        calendar_ids = await manager.calendar_ids()
        return queryset.filter(calendar_id__in=calendar_ids).select_related('created_by').order_by('name', 'id')
