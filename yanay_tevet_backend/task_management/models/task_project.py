from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager

from task_management.enums.project_status import ProjectStatus
from users.models import User

if TYPE_CHECKING:
    from task_management.models.task_project_membership import TaskProjectMembership
    from task_management.models.task import Task


class TaskProject(models.Model):
    if TYPE_CHECKING:
        id: int
        owner_id: int
        memberships: Manager['TaskProjectMembership']
        tasks: Manager['Task']

    list_display = ['id', 'name', 'owner', 'status', 'updated_at']
    list_filter = ['status']
    raw_id_fields = ['owner']

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_task_projects')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    status: ProjectStatus = models.CharField(
        max_length=16,
        choices=ProjectStatus.choices(),
        default=ProjectStatus.ACTIVE,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self) -> str:
        return f'TaskProject({self.id}) - {self.name}'

    async def get_owner(self) -> User | None:
        return await User.objects.filter(id=self.owner_id).afirst()
