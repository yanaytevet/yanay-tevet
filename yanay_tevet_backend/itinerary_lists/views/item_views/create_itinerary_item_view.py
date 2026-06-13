from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from itinerary_lists.managers.itinerary_item_manager import ItineraryItemManager
from itinerary_lists.models.itinerary_item import ItineraryItem
from itinerary_lists.models.itinerary_list import ItineraryList
from itinerary_lists.permissions_checkers.list_member_permission_checker import ListMemberPermissionChecker
from itinerary_lists.serializers.itinerary_item_serializers.itinerary_item_serializer import (
    ItineraryItemSerializer,
    ItineraryItemWritableSchema,
)
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView


class CreateItineraryItemSchema(ItineraryItemWritableSchema):
    itinerary_list_id: int
    name: str


class CreateItineraryItemView(CreateItemAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreateItineraryItemSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return ItineraryItemSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ItineraryItem

    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: CreateItineraryItemSchema, path: Path) -> None:
        itinerary_list = await ItineraryList.objects.filter(id=data.itinerary_list_id).afirst()
        if itinerary_list is None:
            raise ObjectDoesntExistAPIException(ItineraryList, data.itinerary_list_id)
        await ListMemberPermissionChecker(itinerary_list).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def create_object(cls, request: APIRequest, data: CreateItineraryItemSchema, path: Path) -> Model:
        user = await request.future_user
        writable = ItineraryItemWritableSchema(
            **data.model_dump(exclude_unset=True, exclude={'itinerary_list_id'})
        )
        return await ItineraryItemManager(user).create_item(data.itinerary_list_id, writable)
