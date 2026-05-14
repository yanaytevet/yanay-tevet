import inspect
import os
from abc import abstractmethod
from typing import TypeVar, Any, Type, Self

from common.classes_loaders.id_able_class import IdAbleClass
from common.classes_loaders.modules_loader import ModulesLoader

T = TypeVar("T")


class ClassGeneratorMeta(type):
    def __init__(cls: Type['ClassGenerator'], name, bases, dct):
        super().__init__(name, bases, dct)
        if name == 'ClassGenerator':
            return
        cls.load_classes_from_directory()


class ClassGenerator(metaclass=ClassGeneratorMeta):
    ID_TO_CLASS: dict[Any, Type[IdAbleClass]] = {}

    @classmethod
    def get_class_by_id(cls, class_id: Any) -> T:
        return cls.ID_TO_CLASS[class_id]

    @classmethod
    @abstractmethod
    def get_classes_directory_name(cls) -> str:
        raise NotImplementedError()

    @classmethod
    def get_classes_directory_path(cls) -> str:
        return os.path.join(os.path.dirname(inspect.getfile(cls)), cls.get_classes_directory_name())

    @classmethod
    def load_classes_from_directory(cls) -> None:
        cls.ID_TO_CLASS = {}
        klass: Type[Self]
        for klass in ModulesLoader.get_all_classes_from_directory(cls.get_classes_directory_path()):
            cls.register_class(klass)

    @classmethod
    def register_class(cls, klass: Type[IdAbleClass]) -> Type[Self]:
        cls.ID_TO_CLASS[klass.get_class_id()] = klass
        return klass
