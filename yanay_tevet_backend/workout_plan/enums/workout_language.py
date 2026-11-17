from common.base_enum import BaseEnum


# Used only by migration 0002; the language now lives on the user (users.enums.language).
class WorkoutLanguage(BaseEnum):
    ENGLISH = 'en'
    HEBREW = 'he'
