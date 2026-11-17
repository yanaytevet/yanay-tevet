from datetime import datetime
from typing import Optional

from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from workout_plan.models.set_log import SetLog
from workout_plan.models.workout_session import WorkoutSession


class WorkoutSessionSchema(Schema):
    id: int
    plan_id: Optional[int]
    day_id: Optional[int]
    plan_name: str
    day_name: str
    pool_length_m: int
    started_at: datetime
    finished_at: Optional[datetime]
    set_count: int
    exercise_count: int


class WorkoutSessionSerializer(Serializer[WorkoutSessionSchema]):
    async def inner_serialize(self, obj: WorkoutSession) -> WorkoutSessionSchema:
        logs = SetLog.objects.filter(session_id=obj.id)
        return WorkoutSessionSchema(
            id=obj.id,
            plan_id=obj.plan_id,
            day_id=obj.day_id,
            plan_name=obj.plan_name,
            day_name=obj.day_name,
            pool_length_m=obj.pool_length_m,
            started_at=obj.started_at,
            finished_at=obj.finished_at,
            set_count=await logs.acount(),
            exercise_count=await logs.values('exercise_id').distinct().acount(),
        )
