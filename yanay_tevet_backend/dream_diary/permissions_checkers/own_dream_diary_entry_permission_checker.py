from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.permissions_checkers.permissions_checker import PermissionsChecker
from dream_diary.models.dream_diary_entry import DreamDiaryEntry
from users.models import User


class OwnDreamDiaryEntryPermissionChecker(PermissionsChecker):
    def __init__(self, entry: DreamDiaryEntry) -> None:
        self.entry = entry

    async def async_raise_exception_if_not_valid(self, user: User | None) -> None:
        if self.entry.user_id != user.id:
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='You do not own this entry.',
                error_code='not_owner',
            )
