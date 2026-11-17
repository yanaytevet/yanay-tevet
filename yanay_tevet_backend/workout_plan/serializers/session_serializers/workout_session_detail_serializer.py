from datetime import datetime
from typing import Optional

from django.db.models import Q
from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from workout_plan.models.exercise import Exercise
from workout_plan.models.plan_exercise import PlanExercise
from workout_plan.models.set_log import SetLog
from workout_plan.models.workout_session import WorkoutSession
from workout_plan.serializers.exercise_serializers.exercise_serializer import ExerciseSchema, ExerciseSerializer
from workout_plan.serializers.plan_serializers.plan_exercise_serializer import (
    PlanExerciseSchema,
    PlanExerciseSerializer,
)
from workout_plan.serializers.session_serializers.set_log_serializer import SetLogSchema, SetLogSerializer


class WorkoutSessionDetailSchema(Schema):
    id: int
    plan_id: Optional[int]
    day_id: Optional[int]
    plan_name: str
    day_name: str
    pool_length_m: int
    started_at: datetime
    finished_at: Optional[datetime]
    # The every-day section first, then the day's own exercises, as the plan stands now.
    plan_exercises: list[PlanExerciseSchema]
    set_logs: list[SetLogSchema]
    # Exercises logged in this session that are not (or no longer) in the plan.
    extra_exercises: list[ExerciseSchema]
    # For each exercise of the session, the sets of the last earlier session that had it, to prefill from.
    previous_logs: list[SetLogSchema]


class WorkoutSessionDetailSerializer(Serializer[WorkoutSessionDetailSchema]):
    async def inner_serialize(self, obj: WorkoutSession) -> WorkoutSessionDetailSchema:
        plan_exercises = [
            pe async for pe in PlanExercise.objects.filter(
                Q(day__plan_id=obj.plan_id, day__is_every_day=True) | Q(day_id=obj.day_id)
            ).select_related('exercise').order_by('-day__is_every_day', 'order', 'id')
        ] if obj.plan_id is not None else []
        set_logs = [log async for log in SetLog.objects.filter(session_id=obj.id).order_by('set_number', 'side', 'id')]

        planned_exercise_ids = {pe.exercise_id for pe in plan_exercises}
        logged_exercise_ids = list(dict.fromkeys(log.exercise_id for log in set_logs))
        extra_ids = [exercise_id for exercise_id in logged_exercise_ids if exercise_id not in planned_exercise_ids]
        exercise_ids = list(dict.fromkeys([pe.exercise_id for pe in plan_exercises] + extra_ids))

        plan_exercise_serializer = PlanExerciseSerializer()
        set_log_serializer = SetLogSerializer()
        exercise_serializer = ExerciseSerializer()
        extra_by_id = {exercise.id: exercise async for exercise in Exercise.objects.filter(id__in=extra_ids)}
        extra_exercises = [await exercise_serializer.serialize(extra_by_id[exercise_id]) for exercise_id in extra_ids]
        return WorkoutSessionDetailSchema(
            id=obj.id,
            plan_id=obj.plan_id,
            day_id=obj.day_id,
            plan_name=obj.plan_name,
            day_name=obj.day_name,
            pool_length_m=obj.pool_length_m,
            started_at=obj.started_at,
            finished_at=obj.finished_at,
            plan_exercises=[await plan_exercise_serializer.serialize(pe) for pe in plan_exercises],
            set_logs=[await set_log_serializer.serialize(log) for log in set_logs],
            extra_exercises=extra_exercises,
            previous_logs=[
                await set_log_serializer.serialize(log) for log in await self._previous_logs(obj, exercise_ids)
            ],
        )

    @staticmethod
    async def _previous_logs(session: WorkoutSession, exercise_ids: list[int]) -> list[SetLog]:
        previous: list[SetLog] = []
        for exercise_id in exercise_ids:
            last_session_id = await SetLog.objects.filter(
                exercise_id=exercise_id, session__user_id=session.user_id, session__started_at__lt=session.started_at,
            ).order_by('-session__started_at', '-session_id').values_list('session_id', flat=True).afirst()
            if last_session_id is None:
                continue
            previous.extend([
                log async for log in SetLog.objects.filter(session_id=last_session_id, exercise_id=exercise_id)
                .order_by('set_number', 'side', 'id')
            ])
        return previous
