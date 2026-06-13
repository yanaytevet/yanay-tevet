from typing import Optional, Type

from django.db.models import Model
from ninja import Path, Schema

from task_management.managers.task_project_manager import TaskProjectManager
from task_management.models.task_project import TaskProject
from task_management.serializers.task_project_serializers.task_project_serializer import TaskProjectSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.schemas.schema_config import hidden_fields_config
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView


class CreateTaskProjectSchema(Schema):
    model_config = hidden_fields_config('owner_id')
    owner_id: Optional[int] = None
    name: str
    description: str = ''


class CreateTaskProjectView(CreateItemAPIView):
    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreateTaskProjectSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return TaskProjectSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return TaskProject

    @classmethod
    async def modify_creation_data(cls, request: APIRequest, data: CreateTaskProjectSchema, path: Path) -> CreateTaskProjectSchema:
        data.owner_id = (await request.future_user).id
        return data

    @classmethod
    async def run_after_creation(cls, request: APIRequest, obj: TaskProject, data: Schema, path: Path) -> None:
        user = await request.future_user
        await TaskProjectManager(user).ensure_owner_membership(obj)
