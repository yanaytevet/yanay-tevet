from apartment_hunt.enums.project_role import ProjectRole
from apartment_hunt.models.rental_project import RentalProject
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from users.enums.invitation_membership_type import InvitationMembershipType
from users.enums.permissions import Permissions
from users.managers.invitation_manager import InvitationManager, InvitationResult
from users.models import User
from users.schemas.invitation_schema import InvitationMembership


class VillaVillekullaManager:
    """Invite flow for the Villa Villekulla sub-app.

    Delegates to the generic ``InvitationManager``: existing users are granted
    access immediately, while a not-yet-registered email gets a pending
    invitation + email that is applied when they first sign in. Either way the
    invitee receives the app-level VILLA_VILLEKULLA permission plus a project
    membership (COLLABORATOR friend or OWNER co-admin).
    """

    def __init__(self, user: User) -> None:
        self.user = user

    async def _find_user(self, identifier: str) -> User | None:
        target = await User.objects.filter(username__iexact=identifier).afirst()
        if target is None:
            target = await User.objects.filter(email__iexact=identifier).afirst()
        return target

    async def invite(self, project: RentalProject, identifier: str, role: ProjectRole) -> InvitationResult:
        identifier = identifier.strip()
        membership = InvitationMembership(
            type=InvitationMembershipType.RENTAL_PROJECT,
            object_id=project.id,
            role=role.value,
        )

        target = await self._find_user(identifier)
        if target is not None:
            if target.id == project.owner_id:
                raise RestAPIException(
                    status_code=StatusCode.HTTP_400_BAD_REQUEST,
                    message='The owner already has full access to this project.',
                    error_code='cannot_share_with_owner',
                )
            email = target.email
        elif '@' in identifier:
            email = identifier
        else:
            raise RestAPIException(
                status_code=StatusCode.HTTP_404_NOT_FOUND,
                message=f'No user found matching "{identifier}". Invite them by email instead.',
                error_code='user_not_found',
            )

        return await InvitationManager(self.user).invite(
            email=email,
            permissions=[Permissions.VILLA_VILLEKULLA],
            membership=membership,
        )
