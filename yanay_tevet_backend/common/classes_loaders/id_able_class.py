from abc import abstractmethod, ABC
from typing import TypeVar, Any, Type, Self

T = TypeVar("T")


class IdAbleClass(ABC):
    @classmethod
    @abstractmethod
    def get_class_id(cls) -> Any:
        raise NotImplementedError()
