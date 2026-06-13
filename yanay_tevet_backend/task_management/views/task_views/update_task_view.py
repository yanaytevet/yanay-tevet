from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from task_management.managers.task_manager import TaskManager
from task_management.models.task import Task
from task_management.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from task_management.serializers.task_serializers.task_serializer import TaskSerializer, TaskWritableSchema
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.update_views.update_item_by_id_api_view import UpdateItemByIdAPIView


class UpdateTaskView(UpdateItemByIdAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return TaskWritableSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return TaskSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return Task

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: Task, data: Schema, path: Path) -> None:
        project = await obj.get_project()
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def update_object(cls, request: APIRequest, obj: Task, data: TaskWritableSchema, path: Path) -> None:
        user = await request.future_user
        await TaskManager(user).update_task(obj, data)
