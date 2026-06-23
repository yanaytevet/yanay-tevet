from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone

from users.models import User


class DreamDiaryEntry(models.Model):
    if TYPE_CHECKING:
        id: int
        user_id: int

    list_display = ['id', 'user', 'title', 'time']
    list_filter = ['user']
    raw_id_fields = ['user']

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dream_diary_entries')
    title = models.CharField(max_length=255, blank=True, default='')
    text = models.TextField()
    time = models.DateTimeField(default=timezone.now)
    image_url = models.CharField(max_length=1024, blank=True, null=True)

    class Meta:
        ordering = ['-time']

    def __str__(self) -> str:
        return f'DreamDiaryEntry({self.id}) - {self.title or "untitled"} @ {self.time}'

    async def get_user(self) -> User | None:
        return await User.objects.filter(id=self.user_id).afirst()
