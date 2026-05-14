from typing import get_type_hints, Any


class TypeUtils:
    @classmethod
    def is_typeddict(cls, obj: any) -> bool:
        if hasattr(obj, '__total__'):
            return True
        try:
            return '__annotations__' in get_type_hints(obj)
        except Exception:
            return False

    @classmethod
    def stringify_keys(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return {str(k): cls.stringify_keys(v) for k, v in value.items()}
        if isinstance(value, list):
            return [cls.stringify_keys(v) for v in value]
        return value