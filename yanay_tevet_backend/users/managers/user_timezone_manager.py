from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from users.models import User


class UserTimezoneManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def set_timezone(self, timezone_name: str | None) -> User:
        normalized = self._normalize(timezone_name)
        if normalized is not None and not self._is_valid(normalized):
            raise RestAPIException(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                message=f'"{normalized}" is not a valid IANA timezone name.',
                error_code='invalid_timezone',
            )
        self.user.timezone = normalized
        await self.user.asave(update_fields=['timezone'])
        return self.user

    @staticmethod
    def _normalize(timezone_name: str | None) -> str | None:
        if timezone_name is None:
            return None
        stripped = timezone_name.strip()
        return stripped or None

    @staticmethod
    def _is_valid(timezone_name: str) -> bool:
        try:
            ZoneInfo(timezone_name)
            return True
        except (ZoneInfoNotFoundError, ValueError):
            return False
