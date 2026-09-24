from typing import Optional, Type

from django.db.models import Model
from ninja import Path, Schema

from shopping_lists.managers.shopping_list_manager import ShoppingListManager
from shopping_lists.models.shopping_list import ShoppingList
from shopping_lists.serializers.shopping_list_serializers.shopping_list_serializer import ShoppingListSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.schemas.schema_config import hidden_fields_config
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView


class CreateShoppingListSchema(Schema):
    model_config = hidden_fields_config('owner_id')
    owner_id: Optional[int] = None
    name: str


class CreateShoppingListView(CreateItemAPIView):
    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreateShoppingListSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return ShoppingListSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return ShoppingList

    @classmethod
    async def modify_creation_data(cls, request: APIRequest, data: CreateShoppingListSchema, path: Path) -> CreateShoppingListSchema:
        data.owner_id = (await request.future_user).id
        return data

    @classmethod
    async def run_after_creation(cls, request: APIRequest, obj: ShoppingList, data: Schema, path: Path) -> None:
        user = await request.future_user
        await ShoppingListManager(user).ensure_owner_membership(obj)
