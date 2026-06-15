from typing import Self, TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Manager

from common.db_fields.list_field_with_choices import ListFieldWithChoices
from users.enums.permissions import Permissions
from users.enums.subscription_type import SubscriptionType

if TYPE_CHECKING:
    from users.models import EmailAddress

class User(AbstractUser):
    if TYPE_CHECKING:
        id: int
        email_addresses: Manager[EmailAddress]

    list_display = ["id", "username"]
    list_filter = []
    raw_id_fields = []
    ignore_fields = ["groups", "user_permissions"]

    permissions = ListFieldWithChoices(
        choices=Permissions.choices(), blank=True, default=list
    )
    pic_url = models.CharField(max_length=255, blank=True, null=True)
    timezone = models.CharField(max_length=64, blank=True, null=True, default=None)
    is_unsubscribed = models.BooleanField(default=False, blank=True)
    subscription_type = models.CharField(
        max_length=20, choices=SubscriptionType.choices(), default=SubscriptionType.BASIC, blank=True
    )

    def __str__(self) -> str:
        return self.get_full_name()

    @classmethod
    async def async_get_by_username(cls, username: str) -> Self | None:
        return await cls.objects.filter(username=username).afirst()

    def is_admin(self) -> bool:
        return Permissions.ADMIN in self.permissions or self.is_superuser

    def get_initials(self) -> str:
        first_letter = self.first_name[0] if self.first_name else ""
        if not first_letter:
            first_letter = self.username[0] if self.username else ""
        second_letter = self.last_name[0] if self.last_name else ""
        return f"{first_letter}{second_letter}"
