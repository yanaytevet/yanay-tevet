import base64
from datetime import timedelta

import cloudinary.uploader
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils import timezone
from ninja import UploadedFile

from common.generative_ai.image_generative_ai import ImageGenerativeAI
from common.generative_ai.text_generative_ai import TextGenerativeAI
from dream_diary.models.dream_diary_entry import DreamDiaryEntry
from users.models import User


class DreamDiaryEntryManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def get_logged_dates_last_4_weeks(self) -> list[str]:
        cutoff = timezone.now() - timedelta(weeks=4)
        dates: set[str] = set()
        async for entry in DreamDiaryEntry.objects.filter(
            user=self.user, time__gte=cutoff
        ).values('time'):
            dates.add(entry['time'].date().isoformat())
        return sorted(dates)

    async def upload_image(self, entry: DreamDiaryEntry, file: UploadedFile) -> None:
        b64_str = base64.b64encode(file.read()).decode()
        data_uri = f"data:{file.content_type};base64,{b64_str}"
        folder = f"{settings.CLOUDINARY_PATH}/dream_diary/{self.user.id}/{entry.id}/"
        res = await sync_to_async(cloudinary.uploader.upload)(data_uri, folder=folder)
        entry.image_url = res['secure_url']
        await entry.asave()

    async def generate_title(self, entry: DreamDiaryEntry) -> None:
        prompt = (
            f"Generate a short, evocative title (5 words or fewer) for this dream journal entry. "
            f"Return only the title, no quotes, no explanation.\n\nDream: {entry.text}"
        )
        title = await TextGenerativeAI.generate_text(prompt, system_prompt="You are a poetic dream journal assistant.")
        entry.title = title.strip().strip('"').strip("'")
        await entry.asave()

    async def generate_image(self, entry: DreamDiaryEntry) -> None:
        prompt = (
            f"A dreamlike, surreal illustration of the following dream: {entry.text[:800]}. "
            f"Painterly, vivid colors, ethereal atmosphere."
        )
        b64_data = await ImageGenerativeAI.generate_image(prompt)
        data_uri = f"data:image/png;base64,{b64_data}"
        folder = f"{settings.CLOUDINARY_PATH}/dream_diary/{self.user.id}/{entry.id}/"
        res = await sync_to_async(cloudinary.uploader.upload)(data_uri, folder=folder)
        entry.image_url = res['secure_url']
        await entry.asave()
