from users.models import User
from workout_plan.models.exercise import Exercise
from workout_plan.models.set_log import SetLog
from workout_plan.permissions_checkers.usable_exercise_permission_checker import UsableExercisePermissionChecker
from common.simple_api.permissions_checkers.permissions_checker import PermissionsChecker


class ExerciseProgressPermissionChecker(PermissionsChecker):
    """Progress shows only the user's own logs, so having logged the exercise is enough, even if it was a
    collaborator's exercise that has since left the shared plan."""

    def __init__(self, exercise: Exercise) -> None:
        self.exercise = exercise

    async def async_raise_exception_if_not_valid(self, user: User | None) -> None:
        if await SetLog.objects.filter(exercise_id=self.exercise.id, session__user_id=user.id).aexists():
            return
        await UsableExercisePermissionChecker(self.exercise).async_raise_exception_if_not_valid(user)
