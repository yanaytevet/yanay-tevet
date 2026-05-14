from datetime import datetime
from typing import Optional

from ninja import Schema

from dream_diary.models.dream_diary_entry import DreamDiaryEntry
from common.simple_api.serializers.serializer import Serializer


class DreamDiaryEntrySchema(Schema):
    id: int
    title: str
    text: str
    time: datetime
    image_url: Optional[str]


class DreamDiaryEntrySerializer(Serializer[DreamDiaryEntrySchema]):
    async def inner_serialize(self, obj: DreamDiaryEntry) -> DreamDiaryEntrySchema:
        return DreamDiaryEntrySchema(
            id=obj.id,
            title=obj.title,
            text=obj.text,
            time=obj.time,
            image_url=obj.image_url,
        )
