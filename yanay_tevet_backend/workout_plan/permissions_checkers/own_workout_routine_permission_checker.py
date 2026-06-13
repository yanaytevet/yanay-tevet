from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.permissions_checkers.permissions_checker import PermissionsChecker
from users.models import User
from workout_plan.models.workout_routine import WorkoutRoutine


class OwnWorkoutRoutinePermissionChecker(PermissionsChecker):
    def __init__(self, routine: WorkoutRoutine | None) -> None:
        self.routine = routine

    async def async_raise_exception_if_not_valid(self, user: User | None) -> None:
        if self.routine is None or self.routine.user_id != user.id:
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='You do not own this routine.',
                error_code='not_owner',
            )
