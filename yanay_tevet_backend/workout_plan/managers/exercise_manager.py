from django.db.models import Q, QuerySet

from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from users.models import User
from workout_plan.enums.muscle_group import MuscleGroup
from workout_plan.enums.tracking_type import TrackingType
from workout_plan.models.exercise import Exercise
from workout_plan.models.plan_exercise import PlanExercise
from workout_plan.models.set_log import SetLog
from workout_plan.serializers.exercise_serializers.exercise_serializer import ExerciseWritableSchema


class ExerciseManager:
    def __init__(self, user: User) -> None:
        self.user = user

    def visible_exercises(self) -> QuerySet:
        """The catalog, the user's own exercises, and collaborators' exercises used in plans shared with them."""
        return Exercise.objects.filter(
            Q(owner__isnull=True)
            | Q(owner_id=self.user.id)
            | Q(plan_entries__day__plan__memberships__user_id=self.user.id)
        ).distinct().order_by('muscle_group', 'name_en', 'name_he', 'id')

    async def create_custom(self, writable: ExerciseWritableSchema) -> Exercise:
        name_en = (writable.name_en or '').strip()
        name_he = (writable.name_he or '').strip()
        if not name_en and not name_he:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='An exercise needs a name.',
                error_code='exercise_name_required',
            )
        return await Exercise.objects.acreate(
            owner_id=self.user.id,
            name_en=name_en,
            name_he=name_he,
            muscle_group=writable.muscle_group or MuscleGroup.OTHER,
            tracking_type=writable.tracking_type or TrackingType.WEIGHT_REPS,
            per_side=bool(writable.per_side),
        )

    async def update_custom(self, exercise: Exercise, writable: ExerciseWritableSchema) -> None:
        fields = writable.model_dump(exclude_unset=True)
        if 'name_en' in fields:
            exercise.name_en = (writable.name_en or '').strip()
        if 'name_he' in fields:
            exercise.name_he = (writable.name_he or '').strip()
        if not exercise.name_en and not exercise.name_he:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='An exercise needs a name.',
                error_code='exercise_name_required',
            )
        if writable.muscle_group is not None:
            exercise.muscle_group = writable.muscle_group
        if writable.tracking_type is not None and writable.tracking_type != exercise.tracking_type:
            if await SetLog.objects.filter(exercise_id=exercise.id).aexists():
                raise RestAPIException(
                    status_code=StatusCode.HTTP_400_BAD_REQUEST,
                    message='This exercise already has logged sets, so what it tracks cannot change.',
                    error_code='exercise_tracking_type_locked',
                )
            exercise.tracking_type = writable.tracking_type
        if writable.per_side is not None:
            exercise.per_side = writable.per_side
        await exercise.asave()

    async def ensure_deletable(self, exercise: Exercise) -> None:
        if await PlanExercise.objects.filter(exercise_id=exercise.id).aexists():
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='This exercise is in a plan. Remove it from the plan first.',
                error_code='exercise_in_plan',
            )
        if await SetLog.objects.filter(exercise_id=exercise.id).aexists():
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='This exercise has logged workouts, so deleting it would erase your history.',
                error_code='exercise_has_history',
            )
