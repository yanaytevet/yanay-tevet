from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.permissions_checkers.permissions_checker import PermissionsChecker
from users.models import User
from workout_plan.enums.workout_plan_role import WorkoutPlanRole
from workout_plan.models.workout_plan import WorkoutPlan
from workout_plan.models.workout_plan_membership import WorkoutPlanMembership


class WorkoutPlanMemberPermissionChecker(PermissionsChecker):
    """Takes the plan, or just its id when checking a day or an exercise entry that belongs to it."""

    def __init__(self, plan: WorkoutPlan | int, require_owner: bool = False) -> None:
        self.plan_id = plan if isinstance(plan, int) else plan.id
        self.require_owner = require_owner

    async def async_raise_exception_if_not_valid(self, user: User | None) -> None:
        membership = await WorkoutPlanMembership.objects.filter(plan_id=self.plan_id, user_id=user.id).afirst()
        if membership is None:
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='You are not a member of this workout plan.',
                error_code='not_workout_plan_member',
            )
        if self.require_owner and membership.role != WorkoutPlanRole.OWNER:
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='Only the plan owner can do this.',
                error_code='not_workout_plan_owner',
            )
