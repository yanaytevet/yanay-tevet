from typing import Optional

from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from workout_plan.models.exercise import Exercise
from workout_plan.models.plan_exercise import PlanExercise
from workout_plan.serializers.exercise_serializers.exercise_serializer import ExerciseSchema, ExerciseSerializer


class PlanExerciseSchema(Schema):
    id: int
    day_id: int
    exercise: ExerciseSchema
    order: int
    target_sets: int
    target_reps: Optional[int]
    target_weight_kg: Optional[float]
    target_seconds: Optional[int]
    target_distance_km: Optional[float]
    target_laps: Optional[int]
    rest_seconds: int
    notes: str


class PlanExerciseTargetsSchema(Schema):
    """The editable part of a plan exercise. A target sent as null clears it; one left out is kept."""

    target_sets: Optional[int] = None
    target_reps: Optional[int] = None
    target_weight_kg: Optional[float] = None
    target_seconds: Optional[int] = None
    target_distance_km: Optional[float] = None
    target_laps: Optional[int] = None
    rest_seconds: Optional[int] = None
    notes: Optional[str] = None


class PlanExerciseSerializer(Serializer[PlanExerciseSchema]):
    async def inner_serialize(self, obj: PlanExercise) -> PlanExerciseSchema:
        # Callers select_related('exercise'); fall back to a query for an instance loaded without it.
        exercise = obj.exercise if PlanExercise.exercise.is_cached(obj) else await Exercise.objects.aget(id=obj.exercise_id)
        return PlanExerciseSchema(
            id=obj.id,
            day_id=obj.day_id,
            exercise=await ExerciseSerializer().serialize(exercise),
            order=obj.order,
            target_sets=obj.target_sets,
            target_reps=obj.target_reps,
            target_weight_kg=obj.target_weight_kg,
            target_seconds=obj.target_seconds,
            target_distance_km=obj.target_distance_km,
            target_laps=obj.target_laps,
            rest_seconds=obj.rest_seconds,
            notes=obj.notes,
        )
