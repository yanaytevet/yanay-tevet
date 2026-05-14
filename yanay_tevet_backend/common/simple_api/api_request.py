import asyncio
from asyncio import Future

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user
from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpRequest, HttpResponse

from users.managers.django_auth import DjangoAuth
from users.models import User


class APIRequest:
    def __init__(self, original_request: HttpRequest, response: HttpResponse | None = None):
        self.original_request = original_request
        self.response = response
        self.user: User | None = None
        self.future_user: Future[User | None] = Future()

        self.init_user()

    def init_user(self) -> None:
        loop = asyncio.get_event_loop()
        loop.create_task(self.async_init_user())

    async def async_init_user(self) -> None:
        user = await self.async_get_user()
        self.future_user.set_result(user)
        self.user = user

    def set_in_session(self, key: str, value: str) -> None:
        self.original_request.session[key] = value

    async def async_set_in_session(self, key: str, value: any) -> None:
        sync_to_async(self.set_in_session)(key, value)

    async def async_set_as_other(self, is_as_other: bool) -> None:
        await self.async_set_in_session('as_other', is_as_other)

    def get_from_session(self, key: str) -> any:
        return self.original_request.session.get(key)

    async def async_get_from_session(self, key: str) -> any:
        return await sync_to_async(self.get_from_session)(key)

    async def async_get_as_other(self) -> bool:
        return await self.async_get_from_session('as_other')

    async def async_get_user(self) -> User | None:
        return await DjangoAuth.get_user_from_request(self.original_request)

    @property
    def session(self) -> SessionBase:
        return self.original_request.session

    def get_user(self) -> User:
        return get_user(self.original_request)
