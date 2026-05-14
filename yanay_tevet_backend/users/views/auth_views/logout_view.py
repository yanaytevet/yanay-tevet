from django.http import HttpResponse, HttpRequest
from ninja import Router

from users.managers.django_auth import DjangoAuth
from users.schemas.auth_schema import AuthSchema


class LogoutView:
    @classmethod
    def register_post(cls, router: Router, url: str) -> None:
        @router.post(url, tags=['Auth'], operation_id=cls.__name__)
        async def get(request: HttpRequest, response: HttpResponse) -> AuthSchema:
            await DjangoAuth.async_logout(response)
            return AuthSchema(is_authenticated=False, user=None)
