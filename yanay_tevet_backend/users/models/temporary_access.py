from typing import Self, TYPE_CHECKING

from django.db import models

from common.string_utils import StringUtils
from common.time_utils import TimeUtils
from users.enums.temporary_access_types import TemporaryAccessType
from users.models import User


def get_random_hash() -> str:
    return StringUtils.create_random_hash(18)


class TemporaryAccess(models.Model):
    if TYPE_CHECKING:
        id: int
        user_id: int

    TTL_MINUTES = 30

    search_fields = ["id", "user__first_name", "user__last_name"]
    raw_id_fields = ["user"]
    list_filter = []

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    temporary_access_type = models.CharField(
        max_length=30,
        choices=TemporaryAccessType.choices(),
        default=TemporaryAccessType.RESET_PASSWORD,
        blank=True,
    )
    access_id = models.CharField(max_length=18, default=get_random_hash, blank=True)
    creation_time = models.DateTimeField(default=TimeUtils.now)

    @classmethod
    def get_by_user_and_access_id(cls, user_id: int, access_id: str) -> Self | None:
        cls.clean_all_old()
        manager = cls.objects.filter(user_id=user_id, access_id=access_id).order_by(
            "-creation_time"
        )
        return manager.first()

    @classmethod
    def user_id_already_has(cls, user_id: int) -> bool:
        cls.clean_all_old()
        return cls.objects.filter(user_id=user_id).exists()

    @classmethod
    def clean_all_old(cls) -> None:
        now = TimeUtils.now()
        delete_before = TimeUtils.add_minutes_to_time(now, -cls.TTL_MINUTES)
        cls.objects.filter(creation_time__lte=delete_before).delete()

    @classmethod
    def create_for_user(cls, user_obj: User) -> Self:
        obj = cls(user=user_obj)
        obj.save()
        return obj

    async def get_user(self) -> User | None:
        return await User.objects.filter(id=self.user_id).afirst()
