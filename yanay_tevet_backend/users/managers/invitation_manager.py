from asgiref.sync import sync_to_async

from apartment_hunt.models.project_membership import ProjectMembership
from common.time_utils import TimeUtils
from emails.email_templates.invitation_email import InvitationEmail, InvitationEmailContext
from itinerary_lists.models.itinerary_list_membership import ItineraryListMembership
from task_management.models.task_project_membership import TaskProjectMembership
from users.enums.invitation_membership_type import InvitationMembershipType
from users.enums.invitation_status import InvitationStatus
from users.enums.permissions import Permissions
from users.models.invitation import Invitation
from users.models.user import User
from users.schemas.invitation_schema import InvitationMembership


class InvitationResult:
    """Outcome of an invite call, so callers/UI can phrase the response."""

    def __init__(self, applied_immediately: bool, invitation: Invitation | None) -> None:
        self.applied_immediately = applied_immediately
        self.invitation = invitation


class InvitationManager:
    def __init__(self, inviter: User | None = None) -> None:
        self.inviter = inviter

    async def invite(
        self,
        email: str,
        permissions: list[Permissions],
        membership: InvitationMembership | None = None,
    ) -> InvitationResult:
        normalized = Invitation.normalize_email(email)

        existing_user = await User.objects.filter(email__iexact=normalized).afirst()
        if existing_user is not None:
            # Edge case: invitee already has an account — grant access now, no email.
            await self._grant_permissions(existing_user, permissions)
            await self._grant_membership(existing_user, membership)
            return InvitationResult(applied_immediately=True, invitation=None)

        # Edge case: a pending invitation for the same target already exists — merge
        # into it instead of creating a duplicate, and don't re-email.
        match = await self._find_matching_pending(normalized, membership)
        if match is not None:
            await self._merge_into(match, permissions, membership)
            return InvitationResult(applied_immediately=False, invitation=match)

        invitation = await Invitation.objects.acreate(
            email=normalized,
            permissions=[permission.value for permission in permissions],
            membership=membership,
            invited_by=self.inviter,
        )
        await self._send_email(invitation)
        return InvitationResult(applied_immediately=False, invitation=invitation)

    async def list_pending_for_membership(
        self, membership_type: InvitationMembershipType, object_id: int
    ) -> list[Invitation]:
        """Pending invitations whose membership targets the given object."""
        return [
            invitation
            async for invitation in Invitation.objects.filter(
                status=InvitationStatus.PENDING,
                membership__type=membership_type.value,
                membership__object_id=object_id,
            )
        ]

    async def apply_for_user(self, user: User) -> None:
        """Apply every pending invitation addressed to a freshly created user."""
        if not user.email:
            return
        pending = await Invitation.get_pending_for_email(user.email)
        for invitation in pending:
            await self._grant_permissions(
                user, [Permissions(value) for value in invitation.permissions]
            )
            await self._grant_membership(user, invitation.membership)
            invitation.status = InvitationStatus.ACCEPTED
            invitation.accepted_at = TimeUtils.now()
            await invitation.asave(update_fields=['status', 'accepted_at'])

    async def _find_matching_pending(
        self, normalized_email: str, membership: InvitationMembership | None
    ) -> Invitation | None:
        pending = await Invitation.get_pending_for_email(normalized_email)
        for invitation in pending:
            if self._same_membership(invitation.membership, membership):
                return invitation
        return None

    @classmethod
    def _same_membership(
        cls, left: InvitationMembership | None, right: InvitationMembership | None
    ) -> bool:
        if left is None or right is None:
            return left is None and right is None
        return left.type == right.type and left.object_id == right.object_id

    async def _merge_into(
        self,
        invitation: Invitation,
        permissions: list[Permissions],
        membership: InvitationMembership | None,
    ) -> None:
        merged = list(invitation.permissions)
        for permission in permissions:
            if permission.value not in merged:
                merged.append(permission.value)
        invitation.permissions = merged
        if membership is not None:
            invitation.membership = membership
        await invitation.asave(update_fields=['permissions', 'membership'])

    @classmethod
    async def _grant_permissions(cls, user: User, permissions: list[Permissions]) -> None:
        updated = list(user.permissions)
        changed = False
        for permission in permissions:
            if permission.value not in updated:
                updated.append(permission.value)
                changed = True
        if changed:
            user.permissions = updated
            await user.asave(update_fields=['permissions'])

    @classmethod
    async def _grant_membership(cls, user: User, membership: InvitationMembership | None) -> None:
        if membership is None:
            return
        match membership.type:
            case InvitationMembershipType.RENTAL_PROJECT:
                await ProjectMembership.objects.aupdate_or_create(
                    project_id=membership.object_id,
                    user_id=user.id,
                    defaults={'role': membership.role},
                )
            case InvitationMembershipType.TASK_PROJECT:
                await TaskProjectMembership.objects.aupdate_or_create(
                    project_id=membership.object_id,
                    user_id=user.id,
                    defaults={'role': membership.role},
                )
            case InvitationMembershipType.ITINERARY_LIST:
                await ItineraryListMembership.objects.aupdate_or_create(
                    itinerary_list_id=membership.object_id,
                    user_id=user.id,
                    defaults={'role': membership.role},
                )

    async def _send_email(self, invitation: Invitation) -> None:
        inviter_name = self.inviter.get_full_name() if self.inviter is not None else ''
        context = InvitationEmailContext(inviter_name=inviter_name)
        await sync_to_async(InvitationEmail().send_to_address)(context, invitation.email)
