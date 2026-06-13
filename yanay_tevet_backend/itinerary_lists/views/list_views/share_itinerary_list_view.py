from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from itinerary_lists.enums.list_role import ListRole
from itinerary_lists.managers.itinerary_list_manager import ItineraryListManager
from itinerary_lists.models.itinerary_list import ItineraryList
from itinerary_lists.permissions_checkers.list_member_permission_checker import ListMemberPermissionChecker
from itinerary_lists.serializers.itinerary_list_serializers.itinerary_list_serializer import ItineraryListSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.run_action_views.run_action_on_item_by_id_api_view import RunActionOnItemByIdAPIView


class ShareItineraryListSchema(Schema):
    identifier: str
    role: ListRole = ListRole.COLLABORATOR


class ShareItineraryListView(RunActionOnItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ItineraryList

    @classmethod
    def get_serializer(cls) -> Serializer:
        return ItineraryListSerializer()

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return ShareItineraryListSchema

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: ItineraryList, data: Schema, path: Path) -> None:
        await ListMemberPermissionChecker(obj, require_owner=True).async_raise_exception_if_not_valid(
            await request.future_user
        )

    @classmethod
    async def run_action(cls, request: APIRequest, obj: ItineraryList, data: ShareItineraryListSchema, path: Path) -> None:
        user = await request.future_user
        await ItineraryListManager(user).share(obj, data.identifier, data.role)
        return None
