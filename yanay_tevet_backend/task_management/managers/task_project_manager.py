from task_management.enums.project_role import ProjectRole
from task_management.enums.project_status import ProjectStatus
from task_management.models.task_project import TaskProject
from task_management.models.task_project_membership import TaskProjectMembership
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from users.models import User


class TaskProjectManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def ensure_owner_membership(self, project: TaskProject) -> None:
        await TaskProjectMembership.objects.aupdate_or_create(
            project_id=project.id,
            user_id=project.owner_id,
            defaults={'role': ProjectRole.OWNER},
        )

    async def set_status(self, project: TaskProject, status: ProjectStatus) -> None:
        project.status = status
        await project.asave()

    async def _find_user(self, identifier: str) -> User | None:
        identifier = identifier.strip()
        target = await User.objects.filter(username__iexact=identifier).afirst()
        if target is None:
            target = await User.objects.filter(email__iexact=identifier).afirst()
        return target

    async def share(self, project: TaskProject, identifier: str, role: ProjectRole) -> TaskProjectMembership:
        if role == ProjectRole.OWNER:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='Cannot grant the owner role through sharing.',
                error_code='cannot_share_owner_role',
            )
        target = await self._find_user(identifier)
        if target is None:
            raise RestAPIException(
                status_code=StatusCode.HTTP_404_NOT_FOUND,
                message=f'No user found matching "{identifier}".',
                error_code='user_not_found',
            )
        if target.id == project.owner_id:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='The owner already has full access to this project.',
                error_code='cannot_share_with_owner',
            )
        membership, _ = await TaskProjectMembership.objects.aupdate_or_create(
            project_id=project.id,
            user_id=target.id,
            defaults={'role': role},
        )
        return membership

    async def unshare(self, project: TaskProject, identifier: str) -> None:
        target = await self._find_user(identifier)
        if target is None:
            raise RestAPIException(
                status_code=StatusCode.HTTP_404_NOT_FOUND,
                message=f'No user found matching "{identifier}".',
                error_code='user_not_found',
            )
        if target.id == project.owner_id:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='Cannot remove the owner from the project.',
                error_code='cannot_remove_owner',
            )
        await TaskProjectMembership.objects.filter(
            project_id=project.id, user_id=target.id
        ).adelete()

    async def list_members(self, project: TaskProject) -> list[TaskProjectMembership]:
        return [
            m async for m in TaskProjectMembership.objects.filter(
                project_id=project.id
            ).order_by('id')
        ]
