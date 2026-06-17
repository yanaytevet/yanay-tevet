from typing import Type

from django.db.models import Model, QuerySet
from ninja import FilterSchema, Path, Query

from task_management.managers.task_manager import TaskManager
from task_management.models.task_project import TaskProject
from task_management.serializers.task_project_serializers.task_project_serializer import TaskProjectSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.pagination.paginate_items_api_view import PaginateItemsAPIView


class PaginateTaskProjectsFilterSchema(FilterSchema):
    pass


class PaginateTaskProjectsView(PaginateItemsAPIView):
    @classmethod
    async def check_permitted_before_pagination(cls, request: APIRequest, query: Query, path: Path) -> None:
        user = await request.future_user
        await TaskManager(user).reset_all_due_repeating_tasks()

    @classmethod
    def get_serializer(cls) -> Serializer:
        return TaskProjectSerializer()

    @classmethod
    def get_allowed_order_by(cls) -> set[str]:
        return {'id', 'name', 'created_at', 'updated_at'}

    @classmethod
    def get_filter_schema(cls) -> Type[FilterSchema]:
        return PaginateTaskProjectsFilterSchema

    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return TaskProject

    @classmethod
    async def apply_initial_filter_and_order(cls, queryset: QuerySet, request: APIRequest,
                                             query: Query, path: Path) -> QuerySet:
        user = await request.future_user
        return queryset.filter(memberships__user=user).distinct().order_by('-updated_at')
