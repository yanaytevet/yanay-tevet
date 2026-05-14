from django.http import HttpRequest
from ninja import NinjaAPI, Router
from ninja.errors import ValidationError

from common.django_utils.exception_handler import custom_exception_handler
from common.simple_api.permissions_checkers.permissions_checker import PermissionsChecker
from users.managers.django_auth import DjangoAuth
from users.models import User


class ApiRouterCreator:
    @classmethod
    def _make_auth(cls, permission_checker: PermissionsChecker):
        async def auth(request: HttpRequest) -> User | None:
            user = await DjangoAuth.get_user_from_request(request)
            await permission_checker.async_raise_exception_if_not_valid(user)
            return user
        return auth

    @classmethod
    def create_api_and_router(
        cls,
        name: str,
        permission_checker: PermissionsChecker | None = None,
    ) -> tuple[NinjaAPI, Router]:
        api = NinjaAPI(title=name, urls_namespace=name)
        if permission_checker:
            router = Router(auth=cls._make_auth(permission_checker))
        else:
            router = Router()
        api.add_router("", router)
        api.exception_handler(ValidationError)(custom_exception_handler)
        return api, router
