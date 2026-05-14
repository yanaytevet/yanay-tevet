from abc import ABC, abstractmethod
from typing import TypeVar, Generic, get_args

from pydantic import BaseModel

from emails.email_manager import EmailManager
from users.models import User

ContextT = TypeVar('ContextT', bound=BaseModel)


class BaseEmail(ABC, Generic[ContextT]):
    @classmethod
    def get_context_class(cls) -> type[BaseModel]:
        for base in cls.__orig_bases__:
            args = get_args(base)
            if args:
                return args[0]
        raise NotImplementedError(f'{cls.__name__} must declare a context type via BaseEmail[ContextType]')

    @abstractmethod
    def get_template_name(self) -> str: ...

    @abstractmethod
    def get_subject(self) -> str: ...

    def generate_html(self, context: ContextT) -> str:
        return EmailManager.generate_email_html(
            template_name=self.get_template_name(),
            context=context.model_dump(),
        )

    async def send_to_users(self, context: ContextT, users: list[User]) -> None:
        await EmailManager.send_template_to_users(
            template_name=self.get_template_name(),
            subject=self.get_subject(),
            context=context.model_dump(),
            users=users,
        )

    def send_to_address(self, context: ContextT, email_address: str) -> None:
        html = self.generate_html(context)
        EmailManager.send_email_html(
            html=html,
            subject=self.get_subject(),
            email_address=email_address,
        )
