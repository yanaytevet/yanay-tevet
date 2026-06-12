from typing import TYPE_CHECKING

from django.db import models

from apartment_hunt.enums.project_role import ProjectRole
from apartment_hunt.models.rental_project import RentalProject
from users.models import User


class ProjectMembership(models.Model):
    if TYPE_CHECKING:
        id: int
        project_id: int
        user_id: int

    list_display = ['id', 'project', 'user', 'role', 'created_at']
    list_filter = ['role']
    raw_id_fields = ['project', 'user']

    project = models.ForeignKey(RentalProject, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='apartment_hunt_memberships')
    role: ProjectRole = models.CharField(
        max_length=16,
        choices=ProjectRole.choices(),
        default=ProjectRole.COLLABORATOR,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['project', 'user'], name='unique_project_membership'),
        ]
        ordering = ['id']

    def __str__(self) -> str:
        return f'ProjectMembership({self.id}) - project={self.project_id} user={self.user_id} ({self.role})'

    async def get_user(self) -> User | None:
        return await User.objects.filter(id=self.user_id).afirst()
