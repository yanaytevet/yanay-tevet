from datetime import datetime
from typing import Optional

from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from workout_plan.enums.set_side import SetSide
from workout_plan.models.set_log import SetLog


class SetLogSchema(Schema):
    id: int
    session_id: int
    exercise_id: int
    plan_exercise_id: Optional[int]
    set_number: int
    side: SetSide
    reps: Optional[int]
    weight_kg: Optional[float]
    duration_seconds: Optional[int]
    distance_km: Optional[float]
    laps: Optional[int]
    created_at: datetime


class SetLogValuesSchema(Schema):
    """What was done in a set. A value sent as null clears it; one left out is kept."""

    reps: Optional[int] = None
    weight_kg: Optional[float] = None
    duration_seconds: Optional[int] = None
    distance_km: Optional[float] = None
    laps: Optional[int] = None


class SetLogSerializer(Serializer[SetLogSchema]):
    async def inner_serialize(self, obj: SetLog) -> SetLogSchema:
        return SetLogSchema(
            id=obj.id,
            session_id=obj.session_id,
            exercise_id=obj.exercise_id,
            plan_exercise_id=obj.plan_exercise_id,
            set_number=obj.set_number,
            side=SetSide(obj.side),
            reps=obj.reps,
            weight_kg=obj.weight_kg,
            duration_seconds=obj.duration_seconds,
            distance_km=obj.distance_km,
            laps=obj.laps,
            created_at=obj.created_at,
        )
