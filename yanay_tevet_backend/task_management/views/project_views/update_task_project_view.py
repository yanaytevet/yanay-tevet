from typing import Optional, Type

from django.db.models import Model
from ninja import Path, Schema

from task_management.models.task_project import TaskProject
from task_management.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from task_management.serializers.task_project_serializers.task_project_serializer import TaskProjectSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.update_views.update_item_by_id_api_view import UpdateItemByIdAPIView


class UpdateTaskProjectSchema(Schema):
    name: Optional[str] = None
    description: Optional[str] = None


class UpdateTaskProjectView(UpdateItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return UpdateTaskProjectSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return TaskProjectSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return TaskProject

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: TaskProject, data: Schema, path: Path) -> None:
        await ProjectMemberPermissionChecker(obj).async_raise_exception_if_not_valid(await request.future_user)
