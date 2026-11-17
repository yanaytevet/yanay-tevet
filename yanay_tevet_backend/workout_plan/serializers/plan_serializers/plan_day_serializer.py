from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from workout_plan.models.plan_day import PlanDay
from workout_plan.models.plan_exercise import PlanExercise
from workout_plan.serializers.plan_serializers.plan_exercise_serializer import (
    PlanExerciseSchema,
    PlanExerciseSerializer,
)


class PlanDaySchema(Schema):
    id: int
    plan_id: int
    name: str
    is_every_day: bool
    order: int
    exercises: list[PlanExerciseSchema]


class PlanDaySerializer(Serializer[PlanDaySchema]):
    async def inner_serialize(self, obj: PlanDay) -> PlanDaySchema:
        exercises = PlanExercise.objects.filter(day_id=obj.id).select_related('exercise').order_by('order', 'id')
        return PlanDaySchema(
            id=obj.id,
            plan_id=obj.plan_id,
            name=obj.name,
            is_every_day=obj.is_every_day,
            order=obj.order,
            exercises=await PlanExerciseSerializer().serialize_query(exercises),
        )
