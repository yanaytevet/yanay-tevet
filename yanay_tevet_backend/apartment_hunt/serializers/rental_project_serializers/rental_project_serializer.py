from datetime import datetime

from ninja import Schema

from apartment_hunt.enums.currency import Currency
from apartment_hunt.models.rental_project import RentalProject
from common.simple_api.serializers.serializer import Serializer


class RentalProjectSchema(Schema):
    id: int
    name: str
    description: str
    currency: Currency
    owner_id: int
    owner_username: str
    member_count: int
    created_at: datetime
    updated_at: datetime


class RentalProjectSerializer(Serializer[RentalProjectSchema]):
    async def inner_serialize(self, obj: RentalProject) -> RentalProjectSchema:
        owner = await obj.get_owner()
        member_count = await obj.memberships.acount()
        return RentalProjectSchema(
            id=obj.id,
            name=obj.name,
            description=obj.description,
            currency=Currency(obj.currency),
            owner_id=obj.owner_id,
            owner_username=owner.username if owner else '',
            member_count=member_count,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )
