from django.db.models import Count, Max

from users.models import User
from workout_plan.enums.set_side import SetSide
from workout_plan.enums.tracking_type import TrackingType
from workout_plan.models.exercise import Exercise
from workout_plan.models.set_log import SetLog
from workout_plan.models.workout_session import WorkoutSession
from workout_plan.serializers.exercise_serializers.exercise_serializer import ExerciseSerializer
from workout_plan.serializers.progress_serializers.progress_schemas import (
    ExerciseHistorySummarySchema,
    ExerciseProgressSchema,
    ProgressPointSchema,
)


class WorkoutProgressManager:
    """Progress is always the requesting user's own: logs are personal even on a shared plan."""

    def __init__(self, user: User) -> None:
        self.user = user

    async def history_summary(self) -> list[ExerciseHistorySummarySchema]:
        rows = [
            row async for row in SetLog.objects.filter(session__user_id=self.user.id)
            .values('exercise_id')
            .annotate(session_count=Count('session_id', distinct=True), last_started=Max('session__started_at'))
            .order_by('-last_started')
        ]
        exercises = {
            exercise.id: exercise
            async for exercise in Exercise.objects.filter(id__in=[row['exercise_id'] for row in rows])
        }
        serializer = ExerciseSerializer()
        return [
            ExerciseHistorySummarySchema(
                exercise=await serializer.serialize(exercises[row['exercise_id']]),
                session_count=row['session_count'],
                last_date=row['last_started'].date(),
            )
            for row in rows
        ]

    async def exercise_progress(self, exercise: Exercise) -> ExerciseProgressSchema:
        logs_by_session: dict[int, list[SetLog]] = {}
        async for log in SetLog.objects.filter(exercise_id=exercise.id, session__user_id=self.user.id):
            logs_by_session.setdefault(log.session_id, []).append(log)
        sessions = [
            session async for session in WorkoutSession.objects.filter(id__in=list(logs_by_session.keys()))
            .order_by('started_at', 'id')
        ]
        tracking_type = TrackingType(exercise.tracking_type)
        points = [
            self._point(session, logs_by_session[session.id], tracking_type)
            for session in sessions
        ]
        return ExerciseProgressSchema(
            exercise=await ExerciseSerializer().serialize(exercise),
            points=[point for point in points if point is not None],
        )

    @staticmethod
    def _point(session: WorkoutSession, logs: list[SetLog], tracking_type: TrackingType) -> ProgressPointSchema | None:
        point = ProgressPointSchema(session_id=session.id, date=session.started_at.date())
        match tracking_type:
            case TrackingType.WEIGHT_REPS:
                weighted = [log for log in logs if log.weight_kg is not None]
                if not weighted:
                    return None
                point.top_weight_kg = max(log.weight_kg for log in weighted)
                left = [log.weight_kg for log in weighted if log.side == SetSide.LEFT]
                right = [log.weight_kg for log in weighted if log.side == SetSide.RIGHT]
                point.top_weight_left_kg = max(left) if left else None
                point.top_weight_right_kg = max(right) if right else None
                point.volume_kg = round(sum(log.weight_kg * (log.reps or 0) for log in weighted), 2)
                point.total_reps = sum(log.reps or 0 for log in weighted)
            case TrackingType.REPS:
                reps = [log.reps for log in logs if log.reps is not None]
                if not reps:
                    return None
                point.max_reps = max(reps)
                point.total_reps = sum(reps)
            case TrackingType.TIME:
                seconds = [log.duration_seconds for log in logs if log.duration_seconds is not None]
                if not seconds:
                    return None
                point.max_seconds = max(seconds)
                point.total_seconds = sum(seconds)
            case TrackingType.DISTANCE:
                distance = sum(log.distance_km or 0 for log in logs)
                if distance <= 0:
                    return None
                point.distance_km = round(distance, 3)
                timed = [log for log in logs if log.distance_km and log.duration_seconds]
                if timed:
                    point.total_seconds = sum(log.duration_seconds for log in timed)
                    point.pace_seconds_per_km = round(point.total_seconds / sum(log.distance_km for log in timed), 1)
            case TrackingType.LAPS:
                laps = sum(log.laps or 0 for log in logs)
                if laps <= 0:
                    return None
                point.laps = laps
                meters = laps * session.pool_length_m
                point.distance_km = round(meters / 1000, 3)
                timed = [log for log in logs if log.laps and log.duration_seconds]
                if timed:
                    point.total_seconds = sum(log.duration_seconds for log in timed)
                    timed_meters = sum(log.laps for log in timed) * session.pool_length_m
                    point.pace_seconds_per_100m = round(point.total_seconds / timed_meters * 100, 1)
        return point
