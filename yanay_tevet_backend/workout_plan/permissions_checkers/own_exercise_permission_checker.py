from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.permissions_checkers.permissions_checker import PermissionsChecker
from users.models import User
from workout_plan.models.exercise import Exercise


class OwnExercisePermissionChecker(PermissionsChecker):
    """Only a user's own custom exercises can be edited or deleted; the built-in catalog cannot."""

    def __init__(self, exercise: Exercise) -> None:
        self.exercise = exercise

    async def async_raise_exception_if_not_valid(self, user: User | None) -> None:
        if self.exercise.owner_id is None or self.exercise.owner_id != user.id:
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='Only your own exercises can be changed.',
                error_code='not_exercise_owner',
            )
