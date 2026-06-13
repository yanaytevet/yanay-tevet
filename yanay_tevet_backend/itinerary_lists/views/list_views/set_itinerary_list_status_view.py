from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from itinerary_lists.managers.itinerary_list_manager import ItineraryListManager
from itinerary_lists.models.itinerary_list import ItineraryList
from itinerary_lists.permissions_checkers.list_member_permission_checker import ListMemberPermissionChecker
from itinerary_lists.serializers.itinerary_list_serializers.itinerary_list_serializer import ItineraryListSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.schemas.empty_schema import EmptySchema
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.run_action_views.run_action_on_item_by_id_api_view import RunActionOnItemByIdAPIView


class _SetListStatusView(RunActionOnItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ItineraryList

    @classmethod
    def get_serializer(cls) -> Serializer:
        return ItineraryListSerializer()

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return EmptySchema

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: ItineraryList, data: Schema, path: Path) -> None:
        await ListMemberPermissionChecker(obj).async_raise_exception_if_not_valid(await request.future_user)


class ActivateItineraryListView(_SetListStatusView):
    @classmethod
    async def run_action(cls, request: APIRequest, obj: ItineraryList, data: Schema, path: Path) -> None:
        user = await request.future_user
        await ItineraryListManager(user).activate(obj)
        return None


class FinishItineraryListView(_SetListStatusView):
    @classmethod
    async def run_action(cls, request: APIRequest, obj: ItineraryList, data: Schema, path: Path) -> None:
        user = await request.future_user
        await ItineraryListManager(user).finish(obj)
        return None
