from datetime import datetime
from decimal import Decimal
from typing import Optional

from ninja import Schema

from apartment_hunt.enums.currency import Currency
from apartment_hunt.enums.project_app import ProjectApp
from apartment_hunt.enums.project_status import ProjectStatus
from apartment_hunt.models.rental_project import RentalProject
from common.simple_api.serializers.serializer import Serializer


class RentalProjectSchema(Schema):
    id: int
    app: ProjectApp
    name: str
    description: str
    currency: Currency
    status: ProjectStatus
    initial_asked_rent: Optional[float]
    owner_id: int
    owner_username: str
    member_count: int
    created_at: datetime
    updated_at: datetime


def _to_float(value: Optional[Decimal]) -> Optional[float]:
    return float(value) if value is not None else None


class RentalProjectSerializer(Serializer[RentalProjectSchema]):
    async def inner_serialize(self, obj: RentalProject) -> RentalProjectSchema:
        owner = await obj.get_owner()
        member_count = await obj.memberships.acount()
        return RentalProjectSchema(
            id=obj.id,
            app=ProjectApp(obj.app),
            name=obj.name,
            description=obj.description,
            currency=Currency(obj.currency),
            status=ProjectStatus(obj.status),
            initial_asked_rent=_to_float(obj.initial_asked_rent),
            owner_id=obj.owner_id,
            owner_username=owner.username if owner else '',
            member_count=member_count,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
