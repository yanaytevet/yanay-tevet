from datetime import datetime
from typing import Optional

from ninja import Schema

from workout_plan.enums.measurement_type import MeasurementType
from workout_plan.models.exercise_set import ExerciseSet
from workout_plan.models.workout_exercise import WorkoutExercise
from common.simple_api.serializers.serializer import Serializer


class ExerciseSetSchema(Schema):
    id: int
    order: int
    reps: Optional[int]
    duration_seconds: Optional[int]


class ExerciseSetWritableSchema(Schema):
    reps: Optional[int] = None
    duration_seconds: Optional[int] = None


class WorkoutExerciseSchema(Schema):
    id: int
    routine_id: int
    name: str
    measurement_type: MeasurementType
    notes: str
    order: int
    sets: list[ExerciseSetSchema]
    created_at: datetime
    updated_at: datetime


class WorkoutExerciseWritableSchema(Schema):
    name: Optional[str] = None
    measurement_type: Optional[MeasurementType] = None
    notes: Optional[str] = None
    sets: Optional[list[ExerciseSetWritableSchema]] = None


class WorkoutExerciseSerializer(Serializer[WorkoutExerciseSchema]):
    async def inner_serialize(self, obj: WorkoutExercise) -> WorkoutExerciseSchema:
        sets = [
            ExerciseSetSchema(
                id=exercise_set.id,
                order=exercise_set.order,
                reps=exercise_set.reps,
                duration_seconds=exercise_set.duration_seconds,
            )
            async for exercise_set in ExerciseSet.objects.filter(exercise_id=obj.id).order_by('order', 'id')
        ]
        return WorkoutExerciseSchema(
            id=obj.id,
            routine_id=obj.routine_id,
            name=obj.name,
            measurement_type=MeasurementType(obj.measurement_type),
            notes=obj.notes,
            order=obj.order,
            sets=sets,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
