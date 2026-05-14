from ninja import Schema

from users.serializers.user.user_serializer import UserSchema


class AuthSchema(Schema):
    is_authenticated: bool
    msg: str | None = None
    user: UserSchema | None = None
    access_token: str | None = None