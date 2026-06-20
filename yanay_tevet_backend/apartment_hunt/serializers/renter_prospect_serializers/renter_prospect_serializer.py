from datetime import datetime
from decimal import Decimal
from typing import Optional

from ninja import Schema

from apartment_hunt.enums.family_status import FamilyStatus
from apartment_hunt.enums.renter_status import RenterStatus
from apartment_hunt.models.renter_prospect import RenterProspect
from common.simple_api.serializers.serializer import Serializer


class RenterProspectSchema(Schema):
    id: int
    project_id: int
    name: str
    status: RenterStatus
    saw_apartment: bool
    visit_time: Optional[datetime]
    has_animals: bool
    long_term: bool
    family_status: FamilyStatus
    notes: str
    agreed_rent: Optional[float]
    created_at: datetime
    updated_at: datetime


class RenterProspectWritableSchema(Schema):
    name: Optional[str] = None
    status: Optional[RenterStatus] = None
    saw_apartment: Optional[bool] = None
    visit_time: Optional[datetime] = None
    has_animals: Optional[bool] = None
    long_term: Optional[bool] = None
    family_status: Optional[FamilyStatus] = None
    notes: Optional[str] = None
    agreed_rent: Optional[Decimal] = None


def _to_float(value: Optional[Decimal]) -> Optional[float]:
    return float(value) if value is not None else None


class RenterProspectSerializer(Serializer[RenterProspectSchema]):
    async def inner_serialize(self, obj: RenterProspect) -> RenterProspectSchema:
        return RenterProspectSchema(
            id=obj.id,
            project_id=obj.project_id,
            name=obj.name,
            status=RenterStatus(obj.status),
            saw_apartment=obj.saw_apartment,
            visit_time=obj.visit_time,
            has_animals=obj.has_animals,
            long_term=obj.long_term,
            family_status=FamilyStatus(obj.family_status),
            notes=obj.notes,
            agreed_rent=_to_float(obj.agreed_rent),
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
