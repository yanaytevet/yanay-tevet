from typing import Optional, Type

from ninja import Schema

from task_management.managers.task_manager import TaskManager
from task_management.models.task_project import TaskProject
from task_management.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView


class ReorderTasksPath(Schema):
    project_id: int


class ReorderTasksSchema(Schema):
    parent_id: Optional[int] = None
    ordered_ids: list[int]


class ReorderTasksOutput(Schema):
    success: bool


class ReorderTasksView(SimplePostAPIView):
    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return ReorderTasksPath

    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return ReorderTasksSchema

    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return ReorderTasksOutput

    @classmethod
    async def check_permitted(cls, request: APIRequest, data: ReorderTasksSchema,
                              path: ReorderTasksPath = None) -> None:
        project = await TaskProject.objects.filter(id=path.project_id).afirst()
        if project is None:
            raise ObjectDoesntExistAPIException(TaskProject, path.project_id)
        user = await request.future_user
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(user)

    @classmethod
    async def run_action(cls, request: APIRequest, data: ReorderTasksSchema,
                         path: ReorderTasksPath = None) -> ReorderTasksOutput:
        user = await request.future_user
        await TaskManager(user).reorder_tasks(path.project_id, data.parent_id, data.ordered_ids)
        return ReorderTasksOutput(success=True)
