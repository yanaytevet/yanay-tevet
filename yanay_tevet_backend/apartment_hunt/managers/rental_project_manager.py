from apartment_hunt.enums.project_role import ProjectRole
from apartment_hunt.models.project_membership import ProjectMembership
from apartment_hunt.models.rental_project import RentalProject
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from users.models import User


class RentalProjectManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def ensure_owner_membership(self, project: RentalProject) -> None:
        await ProjectMembership.objects.aupdate_or_create(
            project_id=project.id,
            user_id=project.owner_id,
            defaults={'role': ProjectRole.OWNER},
        )

    async def _find_user(self, identifier: str) -> User | None:
        identifier = identifier.strip()
        target = await User.objects.filter(username__iexact=identifier).afirst()
        if target is None:
            target = await User.objects.filter(email__iexact=identifier).afirst()
        return target

    async def share(self, project: RentalProject, identifier: str, role: ProjectRole) -> ProjectMembership:
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
        membership, _ = await ProjectMembership.objects.aupdate_or_create(
            project_id=project.id,
            user_id=target.id,
            defaults={'role': role},
        )
        return membership

    async def unshare(self, project: RentalProject, identifier: str) -> None:
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
        await ProjectMembership.objects.filter(project_id=project.id, user_id=target.id).adelete()

    async def list_members(self, project: RentalProject) -> list[ProjectMembership]:
        return [m async for m in ProjectMembership.objects.filter(project_id=project.id).order_by('id')]
