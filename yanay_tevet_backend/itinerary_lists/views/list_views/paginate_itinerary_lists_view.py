from typing import Type

from django.db.models import F, Model, QuerySet
from ninja import FilterSchema, Path, Query

from itinerary_lists.models.itinerary_list import ItineraryList
from itinerary_lists.serializers.itinerary_list_serializers.itinerary_list_serializer import ItineraryListSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.pagination.paginate_items_api_view import PaginateItemsAPIView


class PaginateItineraryListsFilterSchema(FilterSchema):
    pass


class PaginateItineraryListsView(PaginateItemsAPIView):
    @classmethod
    async def check_permitted_before_pagination(cls, request: APIRequest, query: Query, path: Path) -> None:
        pass

    @classmethod
    def get_serializer(cls) -> Serializer:
        return ItineraryListSerializer()

    @classmethod
    def get_allowed_order_by(cls) -> set[str]:
        return {'id', 'name', 'created_at', 'updated_at'}

    @classmethod
    def get_filter_schema(cls) -> Type[FilterSchema]:
        return PaginateItineraryListsFilterSchema

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ItineraryList

    @classmethod
    async def apply_initial_filter_and_order(cls, queryset: QuerySet, request: APIRequest,
                                             query: Query, path: Path) -> QuerySet:
        user = await request.future_user
        return queryset.filter(memberships__user=user).distinct().order_by(
            F('activated_at').desc(nulls_last=True), '-updated_at'
        )
