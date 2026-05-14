import base64

import cloudinary.uploader
from asgiref.sync import sync_to_async
from django.conf import settings
from ninja import UploadedFile

from users.models import User


class UserProfileImageManager:

    @classmethod
    async def upload_profile_image(cls, user: User, file: UploadedFile) -> None:
        b64_str = base64.b64encode(file.read()).decode()
        data_uri = f"data:{file.content_type};base64,{b64_str}"
        folder = f"{settings.CLOUDINARY_PATH}/users/{user.id}/profile/"
        res = await sync_to_async(cloudinary.uploader.upload)(data_uri, folder=folder)
        user.pic_url = res['secure_url']
        await user.asave()
