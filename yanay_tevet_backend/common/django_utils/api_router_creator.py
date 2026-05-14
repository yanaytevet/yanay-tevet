from ninja import NinjaAPI, Router
from ninja.errors import ValidationError

from common.django_utils.exception_handler import custom_exception_handler


class ApiRouterCreator:
    @classmethod
    def create_api_and_router(cls, name: str) -> tuple[NinjaAPI, Router]:
        api = NinjaAPI(title=name, urls_namespace=name)
        router = Router()
        api.add_router("", router)
        api.exception_handler(ValidationError)(custom_exception_handler)
        return api, router
