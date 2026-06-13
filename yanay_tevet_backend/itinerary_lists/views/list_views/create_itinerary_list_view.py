from typing import Optional, Type

from django.db.models import Model
from ninja import Path, Schema

from itinerary_lists.managers.itinerary_list_manager import ItineraryListManager
from itinerary_lists.models.itinerary_list import ItineraryList
from itinerary_lists.serializers.itinerary_list_serializers.itinerary_list_serializer import ItineraryListSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.schemas.schema_config import hidden_fields_config
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView


class CreateItineraryListSchema(Schema):
    model_config = hidden_fields_config('owner_id')
    owner_id: Optional[int] = None
    name: str
    description: str = ''


class CreateItineraryListView(CreateItemAPIView):
    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreateItineraryListSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return ItineraryListSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ItineraryList

    @classmethod
    async def modify_creation_data(cls, request: APIRequest, data: CreateItineraryListSchema, path: Path) -> CreateItineraryListSchema:
        data.owner_id = (await request.future_user).id
        return data

    @classmethod
    async def run_after_creation(cls, request: APIRequest, obj: ItineraryList, data: Schema, path: Path) -> None:
        user = await request.future_user
        await ItineraryListManager(user).ensure_owner_membership(obj)
