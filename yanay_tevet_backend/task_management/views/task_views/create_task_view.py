from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from task_management.managers.task_manager import TaskManager
from task_management.models.task import Task
from task_management.models.task_project import TaskProject
from task_management.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from task_management.serializers.task_serializers.task_serializer import TaskSerializer, TaskWritableSchema
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.create_views.create_item_api_view import CreateItemAPIView


class CreateTaskSchema(TaskWritableSchema):
    project_id: int
    name: str


class CreateTaskView(CreateItemAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return CreateTaskSchema

    @classmethod
    def get_serializer(cls) -> Serializer:
        return TaskSerializer()

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return Task

    @classmethod
    async def check_permitted_before_creation(cls, request: APIRequest, data: CreateTaskSchema, path: Path) -> None:
        project = await TaskProject.objects.filter(id=data.project_id).afirst()
        if project is None:
            raise ObjectDoesntExistAPIException(TaskProject, data.project_id)
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def create_object(cls, request: APIRequest, data: CreateTaskSchema, path: Path) -> Model:
        user = await request.future_user
        writable = TaskWritableSchema(
            **data.model_dump(exclude_unset=True, exclude={'project_id'})
        )
        return await TaskManager(user).create_task(data.project_id, writable)
