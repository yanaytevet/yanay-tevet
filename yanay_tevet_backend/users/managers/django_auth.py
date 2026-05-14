from datetime import timedelta

import jwt
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpRequest

from common.time_utils import TimeUtils
from users.enums.jwt_token_type import JwtTokenType
from users.models import User
from users.types.jwt_token_payload import JwtTokenPayload


class DjangoAuth:
    JWT_SECRET_KEY: str = settings.JWT_SECRET_KEY
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_TOKEN_KEY = 'refresh_token'
    REFRESH_URL = '/auth/'

    @classmethod
    def authenticate(cls, username: str, password: str) -> User:
        return authenticate(username=username, password=password)

    @classmethod
    async def async_authenticate(cls, username: str, password: str) -> User:
        return await sync_to_async(cls.authenticate)(username, password)

    @classmethod
    async def async_login(cls, response: HttpResponse, user: User) -> None:
        response.set_cookie(
            key=cls.REFRESH_TOKEN_KEY,
            value=cls.create_refresh_token(user.id),
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Strict",
            max_age=cls.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            path=cls.REFRESH_URL,
        )

    @classmethod
    async def async_logout(cls, response: HttpResponse) -> None:
        response.delete_cookie(key=cls.REFRESH_TOKEN_KEY, path=cls.REFRESH_URL)

    @classmethod
    def _create_token(cls, user_id: int, token_type: JwtTokenType, expires_delta: timedelta) -> str:
        now = TimeUtils.now()
        payload: JwtTokenPayload = {
            "user_id": user_id,
            "type": token_type,
            "exp": int((now + expires_delta).timestamp()),
            "iat": int(now.timestamp()),
        }
        token = jwt.encode(payload, cls.JWT_SECRET_KEY, algorithm=cls.JWT_ALGORITHM)
        return token


    @classmethod
    def create_access_token(cls, user_id: int) -> str:
        return cls._create_token(user_id, JwtTokenType.ACCESS, timedelta(minutes=cls.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))


    @classmethod
    def create_refresh_token(cls, user_id: int) -> str:
        return cls._create_token(user_id, JwtTokenType.REFRESH, timedelta(days=cls.JWT_REFRESH_TOKEN_EXPIRE_DAYS))


    @classmethod
    def decode_token(cls, token: str) -> JwtTokenPayload | None:
        try:
            return jwt.decode(token, cls.JWT_SECRET_KEY, algorithms=[cls.JWT_ALGORITHM])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None


    @classmethod
    def verify_token(cls, token: str, expected_type: JwtTokenType = JwtTokenType.ACCESS) -> JwtTokenPayload | None:
        payload = cls.decode_token(token)
        if payload and payload.get("type") == expected_type:
            return payload
        return None


    @classmethod
    def verify_refresh_token_from_request(cls, request: HttpRequest) -> JwtTokenPayload | None:
        token = request.COOKIES.get(cls.REFRESH_TOKEN_KEY)
        return cls.verify_token(token, JwtTokenType.REFRESH)

    @classmethod
    def verify_access_token_from_request(cls, request: HttpRequest) -> JwtTokenPayload | None:
        raw_token = request.headers.get('Authorization')
        if not raw_token:
            return None
        token_arr = raw_token.split(' ', 1)
        if len(token_arr) < 2:
            return None
        return cls.verify_token(token_arr[1], JwtTokenType.ACCESS)

    @classmethod
    async def get_user_from_request(cls, request: HttpRequest) -> User | None:
        payload = cls.verify_access_token_from_request(request)
        if payload:
            return await User.objects.filter(id=payload['user_id']).afirst()
        return None

    @classmethod
    async def get_user_from_access_token(cls, access_token: str) -> User | None:
        payload = cls.verify_token(access_token, JwtTokenType.ACCESS)
        if payload:
            return await User.objects.filter(id=payload['user_id']).afirst()
        return None
