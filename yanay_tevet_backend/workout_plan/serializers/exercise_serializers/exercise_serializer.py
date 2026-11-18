from typing import Optional

from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from workout_plan.enums.muscle_group import MuscleGroup
from workout_plan.enums.tracking_type import TrackingType
from workout_plan.models.exercise import Exercise


class ExerciseSchema(Schema):
    id: int
    name_en: str
    name_he: str
    # Names in the other site languages, keyed by language code; empty for a user's own exercise.
    name_translations: dict[str, str]
    muscle_group: MuscleGroup
    tracking_type: TrackingType
    per_side: bool
    is_custom: bool
    owner_id: Optional[int]


class ExerciseWritableSchema(Schema):
    name_en: Optional[str] = None
    name_he: Optional[str] = None
    muscle_group: Optional[MuscleGroup] = None
    tracking_type: Optional[TrackingType] = None
    per_side: Optional[bool] = None


class ExerciseSerializer(Serializer[ExerciseSchema]):
    async def inner_serialize(self, obj: Exercise) -> ExerciseSchema:
        return ExerciseSchema(
            id=obj.id,
            name_en=obj.name_en,
            name_he=obj.name_he,
            name_translations=obj.name_translations,
            muscle_group=MuscleGroup(obj.muscle_group),
            tracking_type=TrackingType(obj.tracking_type),
            per_side=obj.per_side,
            is_custom=obj.owner_id is not None,
            owner_id=obj.owner_id,
        )
