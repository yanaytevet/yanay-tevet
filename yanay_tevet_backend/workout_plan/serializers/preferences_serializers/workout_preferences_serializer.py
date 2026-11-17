from typing import Optional

from ninja import Schema

from common.simple_api.serializers.serializer import Serializer
from workout_plan.enums.workout_language import WorkoutLanguage
from workout_plan.models.workout_preferences import WorkoutPreferences


class WorkoutPreferencesSchema(Schema):
    # None until the user picks one; the app then follows the browser's language.
    language: Optional[WorkoutLanguage]


class WorkoutPreferencesSerializer(Serializer[WorkoutPreferencesSchema]):
    async def inner_serialize(self, obj: WorkoutPreferences) -> WorkoutPreferencesSchema:
        return WorkoutPreferencesSchema(language=WorkoutLanguage(obj.language))
