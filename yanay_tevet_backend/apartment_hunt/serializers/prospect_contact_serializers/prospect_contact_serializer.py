from ninja import Schema

from apartment_hunt.enums.contact_method import ContactMethod
from apartment_hunt.models.prospect_contact import ProspectContact
from common.simple_api.serializers.serializer import Serializer


class ProspectContactSchema(Schema):
    id: int
    method: ContactMethod
    value: str
    label: str
    order: int


class ProspectContactSerializer(Serializer[ProspectContactSchema]):
    async def inner_serialize(self, obj: ProspectContact) -> ProspectContactSchema:
        return ProspectContactSchema(
            id=obj.id,
            method=ContactMethod(obj.method),
            value=obj.value,
            label=obj.label,
            order=obj.order,
        )
