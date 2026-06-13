from datetime import datetime

from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from users.enums.permissions import Permissions
from users.models import User


class AdminUserOutput(Schema):
    id: int
    username: str
    email: str | None
    full_name: str
    initials: str
    is_admin: bool
    permissions: list[Permissions]
    date_joined: datetime


class AdminUserSerializer(Serializer[AdminUserOutput]):
    async def inner_serialize(self, obj: User) -> AdminUserOutput:
        return AdminUserOutput(
            id=obj.id,
            username=obj.username,
            email=obj.email,
            full_name=obj.get_full_name(),
            initials=obj.get_initials(),
            is_admin=obj.is_admin(),
            permissions=obj.permissions,
            date_joined=obj.date_joined,
        )
