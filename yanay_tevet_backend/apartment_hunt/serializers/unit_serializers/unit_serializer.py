from ninja import Schema

from apartment_hunt.models.unit import Unit
from common.simple_api.serializers.serializer import Serializer


class UnitSchema(Schema):
    id: int
    project_id: int
    name: str
    description: str


class UnitSerializer(Serializer[UnitSchema]):
    async def inner_serialize(self, obj: Unit) -> UnitSchema:
        return UnitSchema(
            id=obj.id,
            project_id=obj.project_id,
            name=obj.name,
            description=obj.description,
        )
