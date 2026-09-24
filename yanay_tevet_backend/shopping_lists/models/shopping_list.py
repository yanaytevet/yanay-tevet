from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager

from users.models import User

if TYPE_CHECKING:
    from shopping_lists.models.shopping_list_membership import ShoppingListMembership
    from shopping_lists.models.shopping_item import ShoppingItem


class ShoppingList(models.Model):
    if TYPE_CHECKING:
        id: int
        owner_id: int
        memberships: Manager['ShoppingListMembership']
        items: Manager['ShoppingItem']

    list_display = ['id', 'name', 'owner', 'updated_at']
    raw_id_fields = ['owner']

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_shopping_lists')
    name = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self) -> str:
        return f'ShoppingList({self.id}) - {self.name}'

    async def get_owner(self) -> User | None:
        return await User.objects.filter(id=self.owner_id).afirst()
