import datetime
from typing import Optional

from ninja import Schema

from workout_plan.serializers.exercise_serializers.exercise_serializer import ExerciseSchema


class ExerciseHistorySummarySchema(Schema):
    exercise: ExerciseSchema
    session_count: int
    last_date: datetime.date


class ProgressPointSchema(Schema):
    """One session's numbers for an exercise. Only the ones that fit its tracking type are filled."""

    session_id: int
    date: datetime.date
    top_weight_kg: Optional[float] = None
    top_weight_left_kg: Optional[float] = None
    top_weight_right_kg: Optional[float] = None
    volume_kg: Optional[float] = None
    max_reps: Optional[int] = None
    total_reps: Optional[int] = None
    max_seconds: Optional[int] = None
    total_seconds: Optional[int] = None
    distance_km: Optional[float] = None
    laps: Optional[int] = None
    pace_seconds_per_km: Optional[float] = None
    pace_seconds_per_100m: Optional[float] = None


class ExerciseProgressSchema(Schema):
    exercise: ExerciseSchema
    points: list[ProgressPointSchema]
