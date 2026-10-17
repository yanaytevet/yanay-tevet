from typing import Any

from django.http import HttpResponse
from django.test import AsyncClient

from users.managers.django_auth import DjangoAuth
from users.models import User


class AuthenticatedClient:
    """An `AsyncClient` that sends a user's access token on every request, for tests that call the API
    over HTTP. The client's own default headers do not reach an ASGI request's `headers`, so each call
    carries the token explicitly."""

    def __init__(self, user: User) -> None:
        self.client = AsyncClient()
        self.headers = {'Authorization': f'Bearer {DjangoAuth.create_access_token(user.id)}'}

    async def get(self, path: str) -> HttpResponse:
        return await self.client.get(path, headers=self.headers)

    async def post(self, path: str, data: Any, **extra: Any) -> HttpResponse:
        return await self.client.post(path, data, headers=self.headers, **extra)

    async def post_json(self, path: str, data: Any) -> HttpResponse:
        return await self.client.post(path, data, content_type='application/json', headers=self.headers)

    async def patch(self, path: str, data: Any, **extra: Any) -> HttpResponse:
        return await self.client.patch(path, data, headers=self.headers, **extra)

    async def delete(self, path: str) -> HttpResponse:
        return await self.client.delete(path, headers=self.headers)
