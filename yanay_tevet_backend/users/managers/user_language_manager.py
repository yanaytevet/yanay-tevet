from users.enums.language import Language
from users.models import User


class UserLanguageManager:
    def __init__(self, user: User) -> None:
        self.user = user

    async def set_language(self, language: Language) -> User:
        self.user.language = language
        await self.user.asave(update_fields=['language'])
        return self.user
