from django.http import HttpResponse, HttpRequest
from ninja import Schema, Router

from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from users.managers.django_auth import DjangoAuth
from users.schemas.auth_schema import AuthSchema
from users.serializers.user.user_serializer import UserSerializer

login_exception = RestAPIException(
    status_code=StatusCode.HTTP_401_UNAUTHORIZED,
    error_code='password_or_username_is_incorrect',
    message='Password or username is incorrect',
)


class LoginSchema(Schema):
    username: str
    password: str


class LoginView:
    @classmethod
    def register_post(cls, router: Router, url: str) -> None:
        @router.post(url, tags=['Auth'], operation_id=cls.__name__, response=AuthSchema)
        async def get(request: HttpRequest,
                      response: HttpResponse,
                      data: LoginSchema) -> AuthSchema:
            raw_username = str(data.username).lower().replace(' ', '')
            password = str(data.password)
            try:
                return await cls.authenticate_user(response, raw_username, password)
            except RestAPIException as e:
                if e == login_exception:
                    return AuthSchema(is_authenticated=False, user=None, msg='Password or username is incorrect')
                return AuthSchema(is_authenticated=False, user=None, msg='Unknown error')

    @classmethod
    async def authenticate_user(cls, response: HttpResponse, username: str, password: str) -> AuthSchema:
        user = await DjangoAuth.async_authenticate(username=username, password=password)

        if user is None:
            raise login_exception

        if user and not user.is_anonymous:
            await DjangoAuth.async_login(response, user)
            return AuthSchema(
                is_authenticated=True,
                user=await UserSerializer().serialize(user),
                access_token=DjangoAuth.create_access_token(user.id)
            )
        else:
            raise login_exception
