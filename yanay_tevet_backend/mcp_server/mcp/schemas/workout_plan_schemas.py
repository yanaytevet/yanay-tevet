from ninja import Schema

from workout_plan.serializers.plan_serializers.plan_exercise_serializer import PlanExerciseTargetsSchema
from workout_plan.serializers.session_serializers.workout_session_serializer import WorkoutSessionSchema


class WorkoutPlanExerciseInput(PlanExerciseTargetsSchema):
    """One exercise on a day. exercise_id comes from list_workout_exercises (or create_workout_exercise).
    Fill only the targets that fit the exercise's tracking_type: reps → target_reps; weight_reps →
    target_reps (+ target_weight_kg if known); time → target_seconds; distance → target_distance_km;
    laps → target_laps. Leave target_reps empty for 'as many as possible' / 'to failure' and say so in
    notes. rest_seconds is the rest timer after each set (default 50)."""

    exercise_id: int


class WorkoutPlanDayInput(Schema):
    name: str
    exercises: list[WorkoutPlanExerciseInput] = []


class WorkoutPlanExerciseChange(PlanExerciseTargetsSchema):
    """Only the fields you include are changed; a target sent as null is cleared."""

    plan_exercise_id: int


class WorkoutSessionList(Schema):
    sessions: list[WorkoutSessionSchema]


class RemovedWorkoutPlanExercisesResult(Schema):
    removed_plan_exercise_ids: list[int]


class DeletedWorkoutPlanDayResult(Schema):
    deleted_day_id: int
    deleted_exercise_count: int
