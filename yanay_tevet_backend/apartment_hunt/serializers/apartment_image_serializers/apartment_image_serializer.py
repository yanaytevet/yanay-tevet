from ninja import Schema

from apartment_hunt.models.apartment_image import ApartmentImage
from common.simple_api.serializers.serializer import Serializer


class ApartmentImageSchema(Schema):
    id: int
    image_url: str
    caption: str
    order: int


class ApartmentImageSerializer(Serializer[ApartmentImageSchema]):
    async def inner_serialize(self, obj: ApartmentImage) -> ApartmentImageSchema:
        return ApartmentImageSchema(
            id=obj.id,
            image_url=obj.image_url,
            caption=obj.caption,
            order=obj.order,
        )
