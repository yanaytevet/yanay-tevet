from typing import Type

from ninja import Path, Query, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.exceptions.object_doesnt_exist_api_exception import ObjectDoesntExistAPIException
from common.simple_api.views.item_by_id_api_mixin import ItemByIdPath
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from users.serializers.invitation.pending_invitation_serializer import (
    PendingInvitationSchema,
    PendingInvitationSerializer,
)
from workout_plan.managers.workout_plan_manager import WorkoutPlanManager
from workout_plan.models.workout_plan import WorkoutPlan
from workout_plan.permissions_checkers.workout_plan_member_permission_checker import (
    WorkoutPlanMemberPermissionChecker,
)
from workout_plan.serializers.plan_serializers.workout_plan_membership_serializer import (
    WorkoutPlanMembershipSchema,
    WorkoutPlanMembershipSerializer,
)


class WorkoutPlanMembersSchema(Schema):
    members: list[WorkoutPlanMembershipSchema]
    pending_invitations: list[PendingInvitationSchema]


class ListWorkoutPlanMembersView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return WorkoutPlanMembersSchema

    @classmethod
    def get_path_args_schema(cls) -> Type[Schema]:
        return ItemByIdPath

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None,
                       path: Path = None) -> WorkoutPlanMembersSchema:
        plan = await WorkoutPlan.objects.filter(id=path.object_id).afirst()
        if plan is None:
            raise ObjectDoesntExistAPIException(WorkoutPlan, path.object_id)
        user = await api_request.future_user
        await WorkoutPlanMemberPermissionChecker(plan).async_raise_exception_if_not_valid(user)
        manager = WorkoutPlanManager(user)
        member_serializer = WorkoutPlanMembershipSerializer()
        pending_serializer = PendingInvitationSerializer()
        return WorkoutPlanMembersSchema(
            members=[await member_serializer.serialize(m) for m in await manager.list_members(plan)],
            pending_invitations=[
                await pending_serializer.serialize(p) for p in await manager.list_pending_invitations(plan)
            ],
        )
