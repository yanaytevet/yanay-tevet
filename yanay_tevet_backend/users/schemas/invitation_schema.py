from ninja import Schema

from users.enums.invitation_membership_type import InvitationMembershipType


class InvitationMembership(Schema):
    """The per-app membership an invitation grants once accepted.

    ``object_id`` is the target project/list id; ``role`` is the app-specific
    role value (e.g. ``ProjectRole.OWNER``) stored as a plain string.
    """

    type: InvitationMembershipType
    object_id: int
    role: str
