from typing import Type

from ninja import Path, Query, Schema

from common.simple_api.api_request import APIRequest
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView
from workout_plan.models.workout_preferences import WorkoutPreferences
from workout_plan.serializers.preferences_serializers.workout_preferences_serializer import (
    WorkoutPreferencesSchema,
    WorkoutPreferencesSerializer,
)


class GetWorkoutPreferencesView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return WorkoutPreferencesSchema

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: Path = None) -> None:
        pass

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None,
                       path: Path = None) -> WorkoutPreferencesSchema:
        user = await api_request.future_user
        preferences = await WorkoutPreferences.objects.filter(user_id=user.id).afirst()
        if preferences is None:
            return WorkoutPreferencesSchema(language=None)
        return await WorkoutPreferencesSerializer().serialize(preferences)
