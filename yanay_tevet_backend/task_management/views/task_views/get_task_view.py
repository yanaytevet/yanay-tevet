from typing import Type

from django.db.models import Model
from ninja import Path, Query

from task_management.managers.task_manager import TaskManager
from task_management.models.task import Task
from task_management.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from task_management.serializers.task_serializers.task_serializer import TaskSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.read_views.read_item_by_id_api_view import ReadItemByIdAPIView


class GetTaskView(ReadItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return Task

    @classmethod
    def get_serializer(cls) -> Serializer:
        return TaskSerializer()

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, query: Query, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: Task, query: Query, path: Path) -> None:
        project = await obj.get_project()
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(await request.future_user)

    @classmethod
    async def run_after_get(cls, request: APIRequest, obj: Task, query: Query, path: Path) -> None:
        await TaskManager.reset_due_repeating_tasks(obj.project_id)
        await obj.arefresh_from_db()
