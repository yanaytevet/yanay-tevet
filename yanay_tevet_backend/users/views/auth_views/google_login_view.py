import asyncio
import json
import re
import urllib.parse
import urllib.request

from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from ninja import Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from users.managers.django_auth import DjangoAuth
from users.models import User
from users.schemas.auth_schema import AuthSchema
from users.serializers.user.user_serializer import UserSerializer

invalid_token_exception = RestAPIException(
    status_code=StatusCode.HTTP_401_UNAUTHORIZED,
    error_code='invalid_google_token',
    message='Invalid Google token',
)


class GoogleLoginSchema(Schema):
    google_code: str


class GoogleLoginView(SimplePostAPIView):

    @classmethod
    def get_data_schema(cls):
        return GoogleLoginSchema

    @classmethod
    def get_output_schema(cls):
        return AuthSchema

    @classmethod
    def get_tags(cls):
        return ['Auth']

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, data: GoogleLoginSchema, path=None) -> None:
        pass

    @classmethod
    async def _exchange_code_for_id_token(cls, code: str) -> str:
        post_data = urllib.parse.urlencode({
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': 'postmessage',
            'grant_type': 'authorization_code',
        }).encode('utf-8')

        def _do_exchange():
            req = urllib.request.Request(
                'https://oauth2.googleapis.com/token',
                data=post_data,
                method='POST',
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode('utf-8'))

        try:
            result = await asyncio.to_thread(_do_exchange)
        except Exception:
            raise invalid_token_exception

        id_token_str = result.get('id_token')
        if not id_token_str:
            raise invalid_token_exception
        return id_token_str

    @classmethod
    async def run_action(cls, api_request: APIRequest, data: GoogleLoginSchema, path=None) -> AuthSchema:
        id_token_str = await cls._exchange_code_for_id_token(data.google_code)
        try:
            id_info = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except Exception:
            raise invalid_token_exception

        email = id_info.get('email', '')
        if not email:
            raise invalid_token_exception

        first_name = id_info.get('given_name', '')
        last_name = id_info.get('family_name', '')
        pic_url = id_info.get('picture', '')

        user = await cls._get_or_create_user(email, first_name, last_name, pic_url)
        await DjangoAuth.async_login(api_request.response, user)
        return AuthSchema(
            is_authenticated=True,
            user=await UserSerializer().serialize(user),
            access_token=DjangoAuth.create_access_token(user.id),
        )

    @classmethod
    async def _get_or_create_user(cls, email: str, first_name: str, last_name: str, pic_url: str) -> User:
        user = await User.objects.filter(email=email).afirst()
        if user:
            return user

        base_username = re.sub(r'[^a-z0-9_]', '_', email.split('@')[0].lower())
        username = base_username
        counter = 1
        while await User.objects.filter(username=username).aexists():
            username = f'{base_username}_{counter}'
            counter += 1

        user = await User.objects.acreate(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            pic_url=pic_url,
        )
        return user
