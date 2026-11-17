from typing import Type

from ninja import Path, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_post_api_view import SimplePostAPIView
from workout_plan.enums.workout_language import WorkoutLanguage
from workout_plan.managers.workout_preferences_manager import WorkoutPreferencesManager
from workout_plan.serializers.preferences_serializers.workout_preferences_serializer import (
    WorkoutPreferencesSchema,
    WorkoutPreferencesSerializer,
)


class UpdateWorkoutPreferencesSchema(Schema):
    language: WorkoutLanguage


class UpdateWorkoutPreferencesView(SimplePostAPIView):
    @classmethod
    def get_data_schema(cls) -> Type[Schema]:
        return UpdateWorkoutPreferencesSchema

    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return WorkoutPreferencesSchema

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, data: Schema, path: Path = None) -> None:
        pass

    @classmethod
    async def run_action(cls, api_request: APIRequest, data: UpdateWorkoutPreferencesSchema,
                         path: Path = None) -> WorkoutPreferencesSchema:
        user = await api_request.future_user
        preferences = await WorkoutPreferencesManager(user).set_language(data.language)
        return await WorkoutPreferencesSerializer().serialize(preferences)
