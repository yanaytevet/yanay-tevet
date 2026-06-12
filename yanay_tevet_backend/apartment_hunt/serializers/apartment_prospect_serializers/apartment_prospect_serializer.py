from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from ninja import Field, Schema

from apartment_hunt.enums.contact_method import ContactMethod
from apartment_hunt.enums.prospect_status import ProspectStatus
from apartment_hunt.models.apartment_prospect import ApartmentProspect
from apartment_hunt.serializers.apartment_image_serializers.apartment_image_serializer import (
    ApartmentImageSchema,
    ApartmentImageSerializer,
)
from apartment_hunt.serializers.prospect_contact_serializers.prospect_contact_serializer import (
    ProspectContactSchema,
    ProspectContactSerializer,
)
from common.simple_api.serializers.serializer import Serializer


class ApartmentProspectSchema(Schema):
    id: int
    project_id: int
    title: str
    status: ProspectStatus
    town: str
    full_address: str
    monthly_rent: Optional[float]
    via_agency: bool
    agency_fee: Optional[float]
    monthly_tax_benefit: Optional[float]
    has_protected_room: bool
    liked_level: Optional[int]
    rooms: Optional[float]
    floor: Optional[int]
    size_sqm: Optional[int]
    available_from: Optional[date]
    listing_url: str
    notes: str
    created_at: datetime
    updated_at: datetime
    images: list[ApartmentImageSchema]
    contacts: list[ProspectContactSchema]


# --- write/input schemas (shared by the create/update views and the prospect manager) ---

class ProspectContactInputSchema(Schema):
    method: ContactMethod = ContactMethod.OTHER
    value: str = ''
    label: str = ''
    order: int = 0


class ApartmentProspectWritableSchema(Schema):
    title: Optional[str] = None
    status: Optional[ProspectStatus] = None
    town: Optional[str] = None
    full_address: Optional[str] = None
    monthly_rent: Optional[Decimal] = None
    via_agency: Optional[bool] = None
    agency_fee: Optional[Decimal] = None
    monthly_tax_benefit: Optional[Decimal] = None
    has_protected_room: Optional[bool] = None
    liked_level: Optional[int] = Field(default=None, ge=1, le=5)
    rooms: Optional[Decimal] = None
    floor: Optional[int] = None
    size_sqm: Optional[int] = None
    available_from: Optional[date] = None
    listing_url: Optional[str] = None
    notes: Optional[str] = None


def _to_float(value: Optional[Decimal]) -> Optional[float]:
    return float(value) if value is not None else None


class ApartmentProspectSerializer(Serializer[ApartmentProspectSchema]):
    async def inner_serialize(self, obj: ApartmentProspect) -> ApartmentProspectSchema:
        image_serializer = ApartmentImageSerializer()
        contact_serializer = ProspectContactSerializer()
        images = [await image_serializer.serialize(img) async for img in obj.images.all()]
        contacts = [await contact_serializer.serialize(c) async for c in obj.contacts.all()]
        return ApartmentProspectSchema(
            id=obj.id,
            project_id=obj.project_id,
            title=obj.title,
            status=ProspectStatus(obj.status),
            town=obj.town,
            full_address=obj.full_address,
            monthly_rent=_to_float(obj.monthly_rent),
            via_agency=obj.via_agency,
            agency_fee=_to_float(obj.agency_fee),
            monthly_tax_benefit=_to_float(obj.monthly_tax_benefit),
            has_protected_room=obj.has_protected_room,
            liked_level=obj.liked_level,
            rooms=_to_float(obj.rooms),
            floor=obj.floor,
            size_sqm=obj.size_sqm,
            available_from=obj.available_from,
            listing_url=obj.listing_url,
            notes=obj.notes,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            images=images,
            contacts=contacts,
        )
