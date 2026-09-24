from typing import TYPE_CHECKING

from django.db import models

from shopping_lists.enums.shopping_list_role import ShoppingListRole
from shopping_lists.models.shopping_list import ShoppingList
from users.models import User


class ShoppingListMembership(models.Model):
    if TYPE_CHECKING:
        id: int
        shopping_list_id: int
        user_id: int

    list_display = ['id', 'shopping_list', 'user', 'role', 'created_at']
    list_filter = ['role']
    raw_id_fields = ['shopping_list', 'user']

    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shopping_list_memberships')
    role: ShoppingListRole = models.CharField(
        max_length=16,
        choices=ShoppingListRole.choices(),
        default=ShoppingListRole.COLLABORATOR,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['shopping_list', 'user'], name='unique_shopping_list_membership'),
        ]
        ordering = ['id']

    def __str__(self) -> str:
        return f'ShoppingListMembership({self.id}) - list={self.shopping_list_id} user={self.user_id} ({self.role})'

    async def get_user(self) -> User | None:
        return await User.objects.filter(id=self.user_id).afirst()
