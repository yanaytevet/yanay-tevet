from users.models import User
from workout_plan.enums.workout_language import WorkoutLanguage
from workout_plan.models.workout_preferences import WorkoutPreferences


class WorkoutPreferencesManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def set_language(self, language: WorkoutLanguage) -> WorkoutPreferences:
        preferences, _ = await WorkoutPreferences.objects.aupdate_or_create(
            user_id=self.user.id, defaults={'language': language},
        )
        return preferences
