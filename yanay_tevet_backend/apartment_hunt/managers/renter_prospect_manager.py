from apartment_hunt.models.renter_prospect import RenterProspect
from apartment_hunt.serializers.renter_prospect_serializers.renter_prospect_serializer import (
    RenterProspectWritableSchema,
)
from common.django_utils.model_utils import ModelUtils
from users.models import User


class RenterProspectManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def create_prospect(
        self,
        project_id: int,
        writable: RenterProspectWritableSchema,
    ) -> RenterProspect:
        prospect = RenterProspect(project_id=project_id, created_by_id=self.user.id)
        await ModelUtils.update_from_schema(prospect, writable)
        await prospect.asave()
        return prospect

    async def update_prospect(
        self,
        prospect: RenterProspect,
        writable: RenterProspectWritableSchema,
    ) -> None:
        await ModelUtils.update_from_schema(prospect, writable)
        await prospect.asave()
