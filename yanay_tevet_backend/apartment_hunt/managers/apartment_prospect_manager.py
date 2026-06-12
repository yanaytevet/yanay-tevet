import base64

import cloudinary.uploader
from asgiref.sync import sync_to_async
from django.conf import settings
from ninja import UploadedFile

from apartment_hunt.models.apartment_image import ApartmentImage
from apartment_hunt.models.apartment_prospect import ApartmentProspect
from apartment_hunt.models.prospect_contact import ProspectContact
from apartment_hunt.serializers.apartment_prospect_serializers.apartment_prospect_serializer import (
    ApartmentProspectWritableSchema,
    ProspectContactInputSchema,
)
from common.django_utils.model_utils import ModelUtils
from users.models import User


class ApartmentProspectManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def create_prospect(
        self,
        project_id: int,
        writable: ApartmentProspectWritableSchema,
        contacts: list[ProspectContactInputSchema],
    ) -> ApartmentProspect:
        prospect = ApartmentProspect(project_id=project_id, created_by_id=self.user.id)
        await ModelUtils.update_from_schema(prospect, writable)
        await prospect.asave()
        await self._replace_contacts(prospect, contacts)
        return prospect

    async def update_prospect(
        self,
        prospect: ApartmentProspect,
        writable: ApartmentProspectWritableSchema,
        contacts: list[ProspectContactInputSchema] | None,
    ) -> None:
        await ModelUtils.update_from_schema(prospect, writable)
        await prospect.asave()
        if contacts is not None:
            await self._replace_contacts(prospect, contacts)

    async def _replace_contacts(
        self, prospect: ApartmentProspect, contacts: list[ProspectContactInputSchema]
    ) -> None:
        await ProspectContact.objects.filter(prospect_id=prospect.id).adelete()
        rows = [
            ProspectContact(
                prospect_id=prospect.id,
                method=contact.method,
                value=contact.value,
                label=contact.label,
                order=contact.order if contact.order else index,
            )
            for index, contact in enumerate(contacts)
        ]
        if rows:
            await ProspectContact.objects.abulk_create(rows)

    async def add_image(self, prospect: ApartmentProspect, file: UploadedFile) -> ApartmentImage:
        b64_str = base64.b64encode(file.read()).decode()
        data_uri = f"data:{file.content_type};base64,{b64_str}"
        folder = f"{settings.CLOUDINARY_PATH}/apartment_hunt/{prospect.project_id}/{prospect.id}/"
        res = await sync_to_async(cloudinary.uploader.upload)(data_uri, folder=folder)
        next_order = await prospect.images.acount()
        return await ApartmentImage.objects.acreate(
            prospect_id=prospect.id,
            image_url=res['secure_url'],
            order=next_order,
        )
