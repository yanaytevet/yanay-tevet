import datetime

from django.utils import timezone

from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from users.models import User
from workout_plan.enums.set_side import SetSide
from workout_plan.models.exercise import Exercise
from workout_plan.models.plan_day import PlanDay
from workout_plan.models.plan_exercise import PlanExercise
from workout_plan.models.set_log import SetLog
from workout_plan.models.workout_plan import WorkoutPlan
from workout_plan.models.workout_session import WorkoutSession
from workout_plan.permissions_checkers.usable_exercise_permission_checker import UsableExercisePermissionChecker
from workout_plan.serializers.session_serializers.set_log_serializer import SetLogValuesSchema

# An unfinished session of the same day this recent is picked up again rather than starting a new one,
# so reopening the page mid-workout doesn't split the workout in two.
RESUME_WINDOW = datetime.timedelta(hours=6)


class WorkoutSessionManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def start(self, plan: WorkoutPlan | None, day: PlanDay | None) -> WorkoutSession:
        day_id = day.id if day is not None and not day.is_every_day else None
        if plan is not None:
            recent = await WorkoutSession.objects.filter(
                user_id=self.user.id, plan_id=plan.id, day_id=day_id, finished_at__isnull=True,
                started_at__gte=timezone.now() - RESUME_WINDOW,
            ).order_by('-started_at').afirst()
            if recent is not None:
                return recent
        return await WorkoutSession.objects.acreate(
            user_id=self.user.id,
            plan_id=plan.id if plan is not None else None,
            day_id=day_id,
            plan_name=plan.name if plan is not None else '',
            day_name=day.name if day is not None and not day.is_every_day else '',
            pool_length_m=plan.pool_length_m if plan is not None else 25,
            started_at=timezone.now(),
        )

    async def set_finished(self, session: WorkoutSession, finished: bool) -> None:
        if finished and session.finished_at is None:
            session.finished_at = timezone.now()
        if not finished:
            session.finished_at = None
        await session.asave()

    async def log_set(
        self,
        session: WorkoutSession,
        exercise: Exercise,
        plan_exercise_id: int | None,
        set_number: int,
        side: SetSide,
        values: SetLogValuesSchema,
    ) -> SetLog:
        """Record a done set. Logging the same set again (same exercise, entry, number and side) updates
        it, so a double tap never makes a duplicate."""
        await UsableExercisePermissionChecker(exercise).async_raise_exception_if_not_valid(self.user)
        if plan_exercise_id is not None:
            plan_exercise = await PlanExercise.objects.filter(id=plan_exercise_id).afirst()
            if plan_exercise is None or plan_exercise.exercise_id != exercise.id:
                raise RestAPIException(
                    status_code=StatusCode.HTTP_400_BAD_REQUEST,
                    message='That plan entry is not this exercise.',
                    error_code='plan_exercise_mismatch',
                )
        set_log = await SetLog.objects.filter(
            session_id=session.id, exercise_id=exercise.id, plan_exercise_id=plan_exercise_id,
            set_number=set_number, side=side,
        ).afirst()
        if set_log is None:
            set_log = SetLog(
                session_id=session.id, exercise_id=exercise.id, plan_exercise_id=plan_exercise_id,
                set_number=max(1, set_number), side=side,
            )
        self._apply_values(set_log, values)
        await set_log.asave()
        await WorkoutSession.objects.filter(id=session.id).aupdate(updated_at=timezone.now())
        return set_log

    async def update_set(self, set_log: SetLog, values: SetLogValuesSchema) -> None:
        self._apply_values(set_log, values)
        await set_log.asave()

    @staticmethod
    def _apply_values(set_log: SetLog, values: SetLogValuesSchema) -> None:
        fields = values.model_dump(exclude_unset=True)
        if 'reps' in fields:
            set_log.reps = values.reps
        if 'weight_kg' in fields:
            set_log.weight_kg = values.weight_kg
        if 'duration_seconds' in fields:
            set_log.duration_seconds = values.duration_seconds
        if 'distance_km' in fields:
            set_log.distance_km = values.distance_km
        if 'laps' in fields:
            set_log.laps = values.laps
