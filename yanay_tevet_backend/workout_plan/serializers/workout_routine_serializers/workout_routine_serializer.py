from datetime import datetime

from ninja import Schema

from workout_plan.models.workout_routine import WorkoutRoutine
from common.simple_api.serializers.serializer import Serializer


class WorkoutRoutineSchema(Schema):
    id: int
    name: str
    order: int
    exercise_count: int
    created_at: datetime
    updated_at: datetime


class WorkoutRoutineSerializer(Serializer[WorkoutRoutineSchema]):
    async def inner_serialize(self, obj: WorkoutRoutine) -> WorkoutRoutineSchema:
        exercise_count = await obj.exercises.acount()
        return WorkoutRoutineSchema(
            id=obj.id,
            name=obj.name,
            order=obj.order,
            exercise_count=exercise_count,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
