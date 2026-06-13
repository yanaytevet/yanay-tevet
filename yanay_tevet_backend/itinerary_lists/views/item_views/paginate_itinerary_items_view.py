from typing import Type

from django.db.models import Model, QuerySet
from ninja import FilterSchema, Path, Query, Schema

from itinerary_lists.models.itinerary_item import ItineraryItem
from itinerary_lists.models.itinerary_list import ItineraryList
from itinerary_lists.permissions_checkers.list_member_permission_checker import ListMemberPermissionChecker
from itinerary_lists.serializers.itinerary_item_serializers.itinerary_item_serializer import ItineraryItemSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.pagination.paginate_items_api_view import PaginateItemsAPIView


class ItemsByListPath(Schema):
    list_id: int


class PaginateItineraryItemsFilterSchema(FilterSchema):
    status: str | None = None


class PaginateItineraryItemsView(PaginateItemsAPIView):
    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return ItemsByListPath

    @classmethod
    async def check_permitted_before_pagination(cls, request: APIRequest, query: Query, path: Path) -> None:
        itinerary_list = await ItineraryList.objects.filter(id=path.list_id).afirst()
        if itinerary_list is None:
            raise ObjectDoesntExistAPIException(ItineraryList, path.list_id)
        await ListMemberPermissionChecker(itinerary_list).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    def get_serializer(cls) -> Serializer:
        return ItineraryItemSerializer()

    @classmethod
    def get_allowed_order_by(cls) -> set[str]:
        return {'id', 'order', 'name', 'status', 'updated_at'}

    @classmethod
    def get_filter_schema(cls) -> Type[FilterSchema]:
        return PaginateItineraryItemsFilterSchema

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ItineraryItem

    @classmethod
    async def apply_initial_filter_and_order(cls, queryset: QuerySet, request: APIRequest,
                                             query: Query, path: Path) -> QuerySet:
        return queryset.filter(itinerary_list_id=path.list_id).order_by('order', 'id')
