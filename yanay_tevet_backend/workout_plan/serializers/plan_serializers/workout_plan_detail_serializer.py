from datetime import datetime
from typing import Optional

from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from workout_plan.models.plan_day import PlanDay
from workout_plan.models.workout_plan import WorkoutPlan
from workout_plan.models.workout_plan_membership import WorkoutPlanMembership
from workout_plan.serializers.plan_serializers.plan_day_serializer import PlanDaySchema, PlanDaySerializer


class WorkoutPlanDetailSchema(Schema):
    id: int
    name: str
    pool_length_m: int
    owner_id: int
    member_count: int
    # Created with the plan (WorkoutPlanManager.create_plan); None only for a plan made some other way.
    every_day: Optional[PlanDaySchema]
    days: list[PlanDaySchema]
    created_at: datetime
    updated_at: datetime


class WorkoutPlanDetailSerializer(Serializer[WorkoutPlanDetailSchema]):
    async def inner_serialize(self, obj: WorkoutPlan) -> WorkoutPlanDetailSchema:
        day_serializer = PlanDaySerializer()
        every_day = await PlanDay.objects.filter(plan_id=obj.id, is_every_day=True).afirst()
        days = PlanDay.objects.filter(plan_id=obj.id, is_every_day=False).order_by('order', 'id')
        return WorkoutPlanDetailSchema(
            id=obj.id,
            name=obj.name,
            pool_length_m=obj.pool_length_m,
            owner_id=obj.owner_id,
            member_count=await WorkoutPlanMembership.objects.filter(plan_id=obj.id).acount(),
            every_day=await day_serializer.serialize(every_day),
            days=await day_serializer.serialize_query(days),
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
