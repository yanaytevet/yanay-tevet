from typing import Type

from ninja import Schema, Path, Query

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from users.managers.django_auth import DjangoAuth
from users.models import User
from users.schemas.auth_schema import AuthSchema
from users.serializers.user.user_serializer import UserSerializer


class AuthView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return AuthSchema

    @classmethod
    async def check_permitted(cls, request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, request: APIRequest, query: Query = None, path: Path = None) -> AuthSchema:
        data = AuthSchema(is_authenticated=False, user=None)
        payload = DjangoAuth.verify_refresh_token_from_request(request.original_request)
        if payload and 'user_id' in payload:
            user_obj = await User.objects.filter(id=payload['user_id']).afirst()
            if cls.is_active_user(user_obj):
                data.is_authenticated = True
                data.user = await UserSerializer().serialize(user_obj)
                data.access_token = DjangoAuth.create_access_token(user_obj.id)
        return data

    @classmethod
    def is_active_user(cls, user_obj: User) -> bool:
        return user_obj and not user_obj.is_anonymous
