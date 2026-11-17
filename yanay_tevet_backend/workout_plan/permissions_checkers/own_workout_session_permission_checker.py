from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.permissions_checkers.permissions_checker import PermissionsChecker
from users.models import User
from workout_plan.models.workout_session import WorkoutSession


class OwnWorkoutSessionPermissionChecker(PermissionsChecker):
    """Logs are personal even on a shared plan: only the user who trained sees or changes a session."""

    def __init__(self, session: WorkoutSession) -> None:
        self.session = session

    async def async_raise_exception_if_not_valid(self, user: User | None) -> None:
        if self.session.user_id != user.id:
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='This workout is not yours.',
                error_code='not_workout_session_owner',
            )
