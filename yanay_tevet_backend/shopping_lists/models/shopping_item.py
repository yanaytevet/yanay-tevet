from typing import TYPE_CHECKING

from django.db import models

from shopping_lists.models.shopping_list import ShoppingList
from users.models import User


class ShoppingItem(models.Model):
    if TYPE_CHECKING:
        id: int
        shopping_list_id: int
        created_by_id: int

    list_display = ['id', 'name', 'shopping_list', 'is_checked', 'order', 'checked_at', 'updated_at']
    list_filter = ['is_checked']
    raw_id_fields = ['shopping_list', 'created_by']

    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name='items')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_shopping_items')

    name = models.CharField(max_length=255)
    is_checked = models.BooleanField(default=False, blank=True)
    checked_at = models.DateTimeField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['is_checked', 'order', 'id']

    def __str__(self) -> str:
        return f'ShoppingItem({self.id}) - {self.name}'

    async def get_shopping_list(self) -> ShoppingList | None:
        return await ShoppingList.objects.filter(id=self.shopping_list_id).afirst()
