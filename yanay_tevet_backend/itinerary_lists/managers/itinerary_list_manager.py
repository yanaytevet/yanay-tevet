from django.utils import timezone

from itinerary_lists.enums.item_status import ItemStatus
from itinerary_lists.enums.list_role import ListRole
from itinerary_lists.enums.list_status import ListStatus
from itinerary_lists.enums.task_status import TaskStatus
from itinerary_lists.models.itinerary_item import ItineraryItem
from itinerary_lists.models.itinerary_list import ItineraryList
from itinerary_lists.models.itinerary_list_membership import ItineraryListMembership
from itinerary_lists.models.itinerary_task import ItineraryTask
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from users.models import User


class ItineraryListManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def ensure_owner_membership(self, itinerary_list: ItineraryList) -> None:
        await ItineraryListMembership.objects.aupdate_or_create(
            itinerary_list_id=itinerary_list.id,
            user_id=itinerary_list.owner_id,
            defaults={'role': ListRole.OWNER},
        )

    async def activate(self, itinerary_list: ItineraryList) -> None:
        itinerary_list.status = ListStatus.ACTIVE
        itinerary_list.activated_at = timezone.now()
        await itinerary_list.asave()

    async def finish(self, itinerary_list: ItineraryList) -> None:
        itinerary_list.status = ListStatus.STANDBY
        itinerary_list.activated_at = None
        await itinerary_list.asave()
        await ItineraryItem.objects.filter(
            itinerary_list_id=itinerary_list.id
        ).exclude(status=ItemStatus.NEED_TO_BUY).aupdate(status=ItemStatus.IN_THE_HOUSE)
        await ItineraryTask.objects.filter(
            itinerary_list_id=itinerary_list.id
        ).aupdate(status=TaskStatus.TO_DO)

    async def _find_user(self, identifier: str) -> User | None:
        identifier = identifier.strip()
        target = await User.objects.filter(username__iexact=identifier).afirst()
        if target is None:
            target = await User.objects.filter(email__iexact=identifier).afirst()
        return target

    async def share(self, itinerary_list: ItineraryList, identifier: str, role: ListRole) -> ItineraryListMembership:
        if role == ListRole.OWNER:
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
        if target.id == itinerary_list.owner_id:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='The owner already has full access to this list.',
                error_code='cannot_share_with_owner',
            )
        membership, _ = await ItineraryListMembership.objects.aupdate_or_create(
            itinerary_list_id=itinerary_list.id,
            user_id=target.id,
            defaults={'role': role},
        )
        return membership

    async def unshare(self, itinerary_list: ItineraryList, identifier: str) -> None:
        target = await self._find_user(identifier)
        if target is None:
            raise RestAPIException(
                status_code=StatusCode.HTTP_404_NOT_FOUND,
                message=f'No user found matching "{identifier}".',
                error_code='user_not_found',
            )
        if target.id == itinerary_list.owner_id:
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message='Cannot remove the owner from the list.',
                error_code='cannot_remove_owner',
            )
        await ItineraryListMembership.objects.filter(
            itinerary_list_id=itinerary_list.id, user_id=target.id
        ).adelete()

    async def list_members(self, itinerary_list: ItineraryList) -> list[ItineraryListMembership]:
        return [
            m async for m in ItineraryListMembership.objects.filter(
                itinerary_list_id=itinerary_list.id
            ).order_by('id')
        ]
