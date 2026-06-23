from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from itinerary_lists.managers.itinerary_task_manager import ItineraryTaskManager
from itinerary_lists.models.itinerary_task import ItineraryTask
from itinerary_lists.permissions_checkers.list_member_permission_checker import ListMemberPermissionChecker
from itinerary_lists.serializers.itinerary_task_serializers.itinerary_task_serializer import (
    ItineraryTaskSerializer,
    ItineraryTaskWritableSchema,
)
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.update_views.update_item_by_id_api_view import UpdateItemByIdAPIView


class UpdateItineraryTaskView(UpdateItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return ItineraryTaskWritableSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return ItineraryTaskSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ItineraryTask

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: ItineraryTask, data: Schema, path: Path) -> None:
        itinerary_list = await obj.get_itinerary_list()
        await ListMemberPermissionChecker(itinerary_list).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def update_object(cls, request: APIRequest, obj: ItineraryTask, data: ItineraryTaskWritableSchema, path: Path) -> None:
        user = await request.future_user
        await ItineraryTaskManager(user).update_task(obj, data)
