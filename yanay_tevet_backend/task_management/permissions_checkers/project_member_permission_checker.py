from task_management.enums.project_role import ProjectRole
from task_management.models.task_project import TaskProject
from task_management.models.task_project_membership import TaskProjectMembership
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.permissions_checkers.permissions_checker import PermissionsChecker
from users.models import User


class ProjectMemberPermissionChecker(PermissionsChecker):
    def __init__(self, project: TaskProject, require_owner: bool = False) -> None:
        self.project = project
        self.require_owner = require_owner

    async def async_raise_exception_if_not_valid(self, user: User | None) -> None:
        membership = await TaskProjectMembership.objects.filter(
            project_id=self.project.id, user_id=user.id
        ).afirst()
        if membership is None:
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='You are not a member of this project.',
                error_code='not_project_member',
            )
        if self.require_owner and membership.role != ProjectRole.OWNER:
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='Only the project owner can perform this action.',
                error_code='not_project_owner',
            )
