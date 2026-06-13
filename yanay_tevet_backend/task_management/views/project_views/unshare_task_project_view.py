from typing import Type

from django.db.models import Model
from ninja import Path, Schema

from task_management.managers.task_project_manager import TaskProjectManager
from task_management.models.task_project import TaskProject
from task_management.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from task_management.serializers.task_project_serializers.task_project_serializer import TaskProjectSerializer
from common.simple_api.api_request import APIRequest
from common.simple_api.serializers.serializer import Serializer
from common.simple_api.views.run_action_views.run_action_on_item_by_id_api_view import RunActionOnItemByIdAPIView


class UnshareTaskProjectSchema(Schema):
    identifier: str


class UnshareTaskProjectView(RunActionOnItemByIdAPIView):
    @classmethod
    def get_model_cls(cls) -> Type[Model]:
        return TaskProject

    @classmethod
    def get_serializer(cls) -> Serializer:
        return TaskProjectSerializer()

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return UnshareTaskProjectSchema

    @classmethod
    async def check_permitted_before_object(cls, request: APIRequest, data: Schema, path: Path) -> None:
        pass

    @classmethod
    async def check_permitted_after_object(cls, request: APIRequest, obj: TaskProject, data: Schema, path: Path) -> None:
        await ProjectMemberPermissionChecker(obj, require_owner=True).async_raise_exception_if_not_valid(
            await request.future_user
        )

    @classmethod
    async def run_action(cls, request: APIRequest, obj: TaskProject, data: UnshareTaskProjectSchema, path: Path) -> None:
        user = await request.future_user
        await TaskProjectManager(user).unshare(obj, data.identifier)
        return None
