from datetime import datetime

from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from users.models.invitation import Invitation


class PendingInvitationSchema(Schema):
    id: int
    email: str
    created_at: datetime


class PendingInvitationSerializer(Serializer[PendingInvitationSchema]):
    async def inner_serialize(self, obj: Invitation) -> PendingInvitationSchema:
        return PendingInvitationSchema(
            id=obj.id,
            email=obj.email,
            created_at=obj.created_at,
        )
