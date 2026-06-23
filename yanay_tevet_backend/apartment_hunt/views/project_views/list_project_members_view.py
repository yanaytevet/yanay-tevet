from typing import Type

from ninja import Path, Query, Schema

from apartment_hunt.managers.rental_project_manager import RentalProjectManager
from apartment_hunt.models.rental_project import RentalProject
from apartment_hunt.permissions_checkers.project_member_permission_checker import ProjectMemberPermissionChecker
from apartment_hunt.serializers.project_membership_serializers.project_membership_serializer import (
    ProjectMembershipSchema,
    ProjectMembershipSerializer,
)
from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.views.item_by_id_api_mixin import ItemByIdPath
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from users.enums.invitation_membership_type import InvitationMembershipType
from users.managers.invitation_manager import InvitationManager
from users.serializers.invitation.pending_invitation_serializer import (
    PendingInvitationSchema,
    PendingInvitationSerializer,
)


class ProjectMembersSchema(Schema):
    members: list[ProjectMembershipSchema]
    pending_invitations: list[PendingInvitationSchema]


class ListProjectMembersView(SimpleGetAPIView):
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
        project = await RentalProject.objects.filter(id=path.object_id).afirst()
        if project is None:
            raise ObjectDoesntExistAPIException(RentalProject, path.object_id)
        user = await api_request.future_user
        await ProjectMemberPermissionChecker(project).async_raise_exception_if_not_valid(user)
        memberships = await RentalProjectManager(user).list_members(project)
        serializer = ProjectMembershipSerializer()
        members = [await serializer.serialize(m) for m in memberships]
        pending = await InvitationManager().list_pending_for_membership(
            InvitationMembershipType.RENTAL_PROJECT, project.id
        )
        pending_serializer = PendingInvitationSerializer()
        pending_invitations = [await pending_serializer.serialize(p) for p in pending]
        return ProjectMembersSchema(members=members, pending_invitations=pending_invitations)
