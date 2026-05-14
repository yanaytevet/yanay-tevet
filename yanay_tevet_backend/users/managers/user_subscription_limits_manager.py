from users.enums.subscription_type import SubscriptionType
from users.models import User
from users.schemas.subscription_limits_schema import SubscriptionLimitsSchema


SUBSCRIPTION_LIMITS: dict[SubscriptionType, SubscriptionLimitsSchema] = {
    SubscriptionType.BASIC: SubscriptionLimitsSchema(items=10),
    SubscriptionType.PRO: SubscriptionLimitsSchema(items=100),
    SubscriptionType.MAX: SubscriptionLimitsSchema(items=1000),
}


class UserSubscriptionLimitsManager:
    def __init__(self, user: User):
        self.user = user

    def get_limits(self) -> SubscriptionLimitsSchema:
        subscription_type = SubscriptionType(self.user.subscription_type)
        return SUBSCRIPTION_LIMITS[subscription_type]

    def get_items_limit(self) -> int:
        return self.get_limits().items
