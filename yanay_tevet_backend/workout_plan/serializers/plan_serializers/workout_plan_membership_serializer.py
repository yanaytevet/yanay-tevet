from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from workout_plan.enums.workout_plan_role import WorkoutPlanRole
from workout_plan.models.workout_plan_membership import WorkoutPlanMembership


class WorkoutPlanMembershipSchema(Schema):
    id: int
    user_id: int
    username: str
    full_name: str
    role: WorkoutPlanRole


class WorkoutPlanMembershipSerializer(Serializer[WorkoutPlanMembershipSchema]):
    async def inner_serialize(self, obj: WorkoutPlanMembership) -> WorkoutPlanMembershipSchema:
        member = await obj.get_user()
        return WorkoutPlanMembershipSchema(
            id=obj.id,
            user_id=obj.user_id,
            username=member.username if member else '',
            full_name=member.get_full_name() if member else '',
            role=WorkoutPlanRole(obj.role),
        )
