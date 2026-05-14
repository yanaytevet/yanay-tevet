from abc import ABC, abstractmethod

from ..exceptions.rest_api_exception import RestAPIException


class PermissionsChecker(ABC):
    @abstractmethod
    async def async_raise_exception_if_not_valid(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    async def async_is_valid(self, *args, **kwargs) -> bool:
        try:
            await self.async_raise_exception_if_not_valid(*args, **kwargs)
        except RestAPIException:
            return False
        return True
