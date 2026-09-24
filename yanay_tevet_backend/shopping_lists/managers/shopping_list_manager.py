from shopping_lists.enums.shopping_list_role import ShoppingListRole
from shopping_lists.models.shopping_list import ShoppingList
from shopping_lists.models.shopping_list_membership import ShoppingListMembership
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from users.enums.invitation_membership_type import InvitationMembershipType
from users.enums.permissions import Permissions
from users.managers.invitation_manager import InvitationManager, InvitationResult
from users.models import Invitation, User
from users.schemas.invitation_schema import InvitationMembership


class ShoppingListManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def ensure_owner_membership(self, shopping_list: ShoppingList) -> None:
        await ShoppingListMembership.objects.aupdate_or_create(
            shopping_list_id=shopping_list.id,
            user_id=shopping_list.owner_id,
            defaults={'role': ShoppingListRole.OWNER},
        )

    async def create_list(self, name: str) -> ShoppingList:
        shopping_list = await ShoppingList.objects.acreate(owner_id=self.user.id, name=name)
        await self.ensure_owner_membership(shopping_list)
        return shopping_list

    async def rename(self, shopping_list: ShoppingList, name: str) -> None:
        shopping_list.name = name
        await shopping_list.asave()

    async def _find_user(self, identifier: str) -> User | None:
        target = await User.objects.filter(username__iexact=identifier).afirst()
        if target is None:
            target = await User.objects.filter(email__iexact=identifier).afirst()
        return target

    async def share(self, shopping_list: ShoppingList, identifier: str) -> InvitationResult:
        """Existing users get access right away; an unknown email gets a pending invitation + email.

        Either way the invitee is also granted the app-level SHOPPING_LISTS permission,
        so they can actually open the list they were added to.
        """
        identifier = identifier.strip()
        target = await self._find_user(identifier)
        if target is not None:
            if target.id == shopping_list.owner_id:
                raise RestAPIException(
                    status_code=StatusCode.HTTP_400_BAD_REQUEST,
                    message='The owner already has full access to this list.',
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

        membership = InvitationMembership(
            type=InvitationMembershipType.SHOPPING_LIST,
            object_id=shopping_list.id,
            role=ShoppingListRole.COLLABORATOR.value,
        )
        return await InvitationManager(self.user).invite(
            email=email,
            permissions=[Permissions.SHOPPING_LISTS],
            membership=membership,
        )

    async def unshare(self, shopping_list: ShoppingList, identifier: str) -> None:
        target = await self._find_user(identifier.strip())
        if target is None:
            raise RestAPIException(
                status_code=StatusCode.HTTP_404_NOT_FOUND,
                message=f'No user found matching "{identifier}".',
                error_code='user_not_found',
            )
        if target.id == shopping_list.owner_id:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='Cannot remove the owner from the list.',
                error_code='cannot_remove_owner',
            )
        await ShoppingListMembership.objects.filter(
            shopping_list_id=shopping_list.id, user_id=target.id
        ).adelete()

    async def list_members(self, shopping_list: ShoppingList) -> list[ShoppingListMembership]:
        return [
            m async for m in ShoppingListMembership.objects.filter(
                shopping_list_id=shopping_list.id
            ).order_by('id')
        ]

    async def list_pending_invitations(self, shopping_list: ShoppingList) -> list[Invitation]:
        return await InvitationManager().list_pending_for_membership(
            InvitationMembershipType.SHOPPING_LIST, shopping_list.id
        )
