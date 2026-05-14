import os
from typing import Type

from common.classes_loaders.modules_loader import ModulesLoader
from emails.base_email import BaseEmail


class EmailClassesLoader:
    @classmethod
    def get_email_classes(cls) -> dict[str, Type[BaseEmail]]:
        templates_dir = os.path.join(os.path.dirname(__file__), 'email_templates')
        result = {}
        for klass in ModulesLoader.get_all_classes_from_directory(templates_dir):
            if inspect_is_email_class(klass):
                result[klass.__name__] = klass
        return result

    @classmethod
    def get_email_class(cls, class_name: str) -> Type[BaseEmail] | None:
        return cls.get_email_classes().get(class_name)


def inspect_is_email_class(klass: type) -> bool:
    try:
        return issubclass(klass, BaseEmail) and klass is not BaseEmail
    except TypeError:
        return False
