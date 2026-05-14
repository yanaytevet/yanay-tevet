from datetime import datetime
from typing import Type, Optional

from django.db.models import Model
from ninja import Schema, Path
from pydantic import ConfigDict

from dream_diary.models.dream_diary_entry import DreamDiaryEntry
from dream_diary.serializers.dream_diary_entry_serializers.dream_diary_entry_serializer import DreamDiaryEntrySerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView


class CreateDreamDiaryEntrySchema(Schema):
    model_config = ConfigDict(
        json_schema_extra=lambda schema: schema.get('properties', {}).pop('user_id', None),
    )
    user_id: Optional[int] = None
    title: Optional[str] = ''
    text: str
    time: datetime


class CreateDreamDiaryEntryView(CreateItemAPIView):
    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreateDreamDiaryEntrySchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return DreamDiaryEntrySerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return DreamDiaryEntry

    @classmethod
    async def modify_creation_data(cls, request: APIRequest, data: CreateDreamDiaryEntrySchema, path: Path) -> CreateDreamDiaryEntrySchema:
        data.user_id = (await request.future_user).id
        return data
