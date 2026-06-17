from typing import Type

from django.db.models import Model, QuerySet
from ninja import FilterSchema, Path, Query, Schema

from task_management.managers.task_manager import TaskManager
from task_management.models.task import Task
from task_management.models.task_project import TaskProject
from task_management.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from task_management.serializers.task_serializers.task_serializer import TaskSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.pagination.paginate_items_api_view import PaginateItemsAPIView


class TasksByProjectPath(Schema):
    project_id: int


class PaginateTasksFilterSchema(FilterSchema):
    status: str | None = None
    priority: str | None = None


class PaginateTasksView(PaginateItemsAPIView):
    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return TasksByProjectPath

    @classmethod
    async def check_permitted_before_pagination(cls, request: APIRequest, query: Query, path: Path) -> None:
        project = await TaskProject.objects.filter(id=path.project_id).afirst()
        if project is None:
            raise ObjectDoesntExistAPIException(TaskProject, path.project_id)
        user = await request.future_user
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(user)

    @classmethod
    async def run_before_pagination(cls, request: APIRequest, query: Query, path: Path) -> None:
        user = await request.future_user
        await TaskManager(user).reset_all_due_repeating_tasks()

    @classmethod
    def get_serializer(cls) -> Serializer:
        return TaskSerializer()

    @classmethod
    def get_allowed_order_by(cls) -> set[str]:
        return {'id', 'order', 'name', 'status', 'priority', 'due_at', 'updated_at'}

    @classmethod
    def get_filter_schema(cls) -> Type[FilterSchema]:
        return PaginateTasksFilterSchema

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return Task

    @classmethod
    async def apply_initial_filter_and_order(cls, queryset: QuerySet, request: APIRequest,
                                             query: Query, path: Path) -> QuerySet:
        return queryset.filter(project_id=path.project_id).order_by('order', 'id')
