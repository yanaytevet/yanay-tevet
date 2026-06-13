from itinerary_lists.enums.list_role import ListRole
from itinerary_lists.models.itinerary_list import ItineraryList
from itinerary_lists.models.itinerary_list_membership import ItineraryListMembership
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.permissions_checkers.permissions_checker import PermissionsChecker
from users.models import User


class ListMemberPermissionChecker(PermissionsChecker):
    def __init__(self, itinerary_list: ItineraryList, require_owner: bool = False) -> None:
        self.itinerary_list = itinerary_list
        self.require_owner = require_owner

    async def async_raise_exception_if_not_valid(self, user: User | None) -> None:
        membership = await ItineraryListMembership.objects.filter(
            itinerary_list_id=self.itinerary_list.id, user_id=user.id
        ).afirst()
        if membership is None:
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='You are not a member of this list.',
                error_code='not_list_member',
            )
        if self.require_owner and membership.role != ListRole.OWNER:
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='Only the list owner can perform this action.',
                error_code='not_list_owner',
            )
