from typing import Type

from ninja import Path, Query, Schema

from task_management.managers.task_project_manager import TaskProjectManager
from task_management.models.task_project import TaskProject
from task_management.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from task_management.serializers.project_membership_serializers.project_membership_serializer import (
    ProjectMembershipSchema,
    ProjectMembershipSerializer,
)
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.views.item_by_id_api_mixin import ItemByIdPath
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView


class ProjectMembersSchema(Schema):
    members: list[ProjectMembershipSchema]


class ListTaskProjectMembersView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return ProjectMembersSchema

    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return ItemByIdPath

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> ProjectMembersSchema:
        project = await TaskProject.objects.filter(id=path.object_id).afirst()
        if project is None:
            raise ObjectDoesntExistAPIException(TaskProject, path.object_id)
        user = await api_request.future_user
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(user)
        memberships = await TaskProjectManager(user).list_members(project)
        serializer = ProjectMembershipSerializer()
        members = [await serializer.serialize(m) for m in memberships]
        return ProjectMembersSchema(members=members)
