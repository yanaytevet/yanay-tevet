from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from users.enums.permissions import Permissions
from users.managers.user_subscription_limits_manager import UserSubscriptionLimitsManager
from users.models import User
from users.schemas.subscription_limits_schema import SubscriptionLimitsSchema


class UserSchema(Schema):
    id: int
    username: str
    email: str | None
    first_name: str
    last_name: str
    pic_url: str | None
    full_name: str
    is_admin: bool
    initials: str
    permissions: list[Permissions]
    subscription_limits: SubscriptionLimitsSchema
    has_usable_password: bool


class UserSerializer(Serializer[UserSchema]):
    async def inner_serialize(self, obj: User) -> UserSchema:
        limits = UserSubscriptionLimitsManager(obj).get_limits()
        return UserSchema(
            id=obj.id,
            username=obj.username,
            email=obj.email,
            first_name=obj.first_name,
            last_name=obj.last_name,
            pic_url=obj.pic_url,
            full_name=obj.get_full_name(),
            is_admin=obj.is_admin(),
            initials=obj.get_initials(),
            permissions=obj.permissions,
            subscription_limits=limits,
            has_usable_password=bool(obj.password) and obj.has_usable_password(),
        )
