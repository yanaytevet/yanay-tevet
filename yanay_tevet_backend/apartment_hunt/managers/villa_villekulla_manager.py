from apartment_hunt.enums.project_role import ProjectRole
from apartment_hunt.models.project_membership import ProjectMembership
from apartment_hunt.models.rental_project import RentalProject
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from users.enums.permissions import Permissions
from users.models import User


class VillaVillekullaManager:
    """Invite flow for the Villa Villekulla sub-app.

    Unlike the generic project share, this grants the app-level
    VILLA_VILLEKULLA permission as part of the invite, so the project owner
    can onboard a friend (COLLABORATOR) or co-admin (OWNER) in one step.
    """

    def __init__(self, user: User) -> None:
        self.user = user

    async def _find_user(self, identifier: str) -> User | None:
        identifier = identifier.strip()
        target = await User.objects.filter(username__iexact=identifier).afirst()
        if target is None:
            target = await User.objects.filter(email__iexact=identifier).afirst()
        return target

    async def invite(self, project: RentalProject, identifier: str, role: ProjectRole) -> ProjectMembership:
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
        if Permissions.VILLA_VILLEKULLA.value not in target.permissions:
            target.permissions = [*target.permissions, Permissions.VILLA_VILLEKULLA.value]
            await target.asave(update_fields=['permissions'])
        membership, _ = await ProjectMembership.objects.aupdate_or_create(
            project_id=project.id,
            user_id=target.id,
            defaults={'role': role},
        )
        return membership
