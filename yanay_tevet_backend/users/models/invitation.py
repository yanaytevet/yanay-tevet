from typing import Self, TYPE_CHECKING

from django.db import models

from common.db_fields.list_field_with_choices import ListFieldWithChoices
from common.db_fields.schema_field import SchemaField
from common.string_utils import StringUtils
from common.time_utils import TimeUtils
from users.enums.invitation_status import InvitationStatus
from users.enums.permissions import Permissions
from users.models.user import User
from users.schemas.invitation_schema import InvitationMembership


def get_random_token() -> str:
    return StringUtils.create_random_hash(24)


class Invitation(models.Model):
    if TYPE_CHECKING:
        id: int
        invited_by_id: int | None

    list_display = ['id', 'email', 'status', 'invited_by', 'created_at']
    list_filter = ['status']
    search_fields = ['id', 'email']
    raw_id_fields = ['invited_by']

    email = models.CharField(max_length=255, db_index=True)
    permissions = ListFieldWithChoices(choices=Permissions.choices(), blank=True, default=list)
    membership: InvitationMembership | None = SchemaField(
        InvitationMembership, null=True, blank=True, default=None
    )
    invited_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_invitations'
    )
    token = models.CharField(max_length=24, default=get_random_token, blank=True)
    status = models.CharField(
        max_length=16, choices=InvitationStatus.choices(), default=InvitationStatus.PENDING, blank=True
    )
    created_at = models.DateTimeField(default=TimeUtils.now)
    accepted_at = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'Invitation({self.id}) - {self.email} ({self.status})'

    @classmethod
    def normalize_email(cls, email: str) -> str:
        return email.strip().lower()

    @classmethod
    async def get_pending_for_email(cls, email: str) -> list[Self]:
        normalized = cls.normalize_email(email)
        return [
            invitation
            async for invitation in cls.objects.filter(email=normalized, status=InvitationStatus.PENDING)
        ]
