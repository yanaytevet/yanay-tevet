from datetime import datetime

from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from workout_plan.models.plan_day import PlanDay
from workout_plan.models.workout_plan import WorkoutPlan
from workout_plan.models.workout_plan_membership import WorkoutPlanMembership


class WorkoutPlanSchema(Schema):
    id: int
    name: str
    pool_length_m: int
    owner_id: int
    day_names: list[str]
    member_count: int
    created_at: datetime
    updated_at: datetime


class WorkoutPlanSerializer(Serializer[WorkoutPlanSchema]):
    async def inner_serialize(self, obj: WorkoutPlan) -> WorkoutPlanSchema:
        day_names = [
            name async for name in PlanDay.objects.filter(plan_id=obj.id, is_every_day=False)
            .order_by('order', 'id').values_list('name', flat=True)
        ]
        return WorkoutPlanSchema(
            id=obj.id,
            name=obj.name,
            pool_length_m=obj.pool_length_m,
            owner_id=obj.owner_id,
            day_names=day_names,
            member_count=await WorkoutPlanMembership.objects.filter(plan_id=obj.id).acount(),
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
