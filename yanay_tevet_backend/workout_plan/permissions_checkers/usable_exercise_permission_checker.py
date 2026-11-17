from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.permissions_checkers.permissions_checker import PermissionsChecker
from users.models import User
from workout_plan.models.exercise import Exercise
from workout_plan.models.plan_exercise import PlanExercise


class UsableExercisePermissionChecker(PermissionsChecker):
    """An exercise a user may put in a plan or log: a built-in one, their own, or one already in a plan
    they are a member of (a collaborator's custom exercise)."""

    def __init__(self, exercise: Exercise) -> None:
        self.exercise = exercise

    async def async_raise_exception_if_not_valid(self, user: User | None) -> None:
        if self.exercise.owner_id is None or self.exercise.owner_id == user.id:
            return
        in_shared_plan = await PlanExercise.objects.filter(
            exercise_id=self.exercise.id, day__plan__memberships__user_id=user.id,
        ).aexists()
        if not in_shared_plan:
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='You cannot use this exercise.',
                error_code='exercise_not_usable',
            )
