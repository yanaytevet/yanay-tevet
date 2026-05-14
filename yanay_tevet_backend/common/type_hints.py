from typing import Union, Any

JSONType = Union[None, int, str, bool, list[Any], dict[str, Any]]
OptionalJSONType = JSONType | None
