from typing import Type

from django.db.models import Model
from ninja import Path, Query

from itinerary_lists.models.itinerary_list import ItineraryList
from itinerary_lists.permissions_checkers.list_member_permission_checker import ListMemberPermissionChecker
from itinerary_lists.serializers.itinerary_list_serializers.itinerary_list_serializer import ItineraryListSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.read_views.read_item_by_id_api_view import ReadItemByIdAPIView


class GetItineraryListView(ReadItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ItineraryList

    @classmethod
    def get_serializer(cls) -> Serializer:
        return ItineraryListSerializer()

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, query: Query, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: ItineraryList, query: Query, path: Path) -> None:
        await ListMemberPermissionChecker(obj).async_raise_exception_if_not_valid(await request.future_user)
