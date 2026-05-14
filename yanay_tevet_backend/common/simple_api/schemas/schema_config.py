from pydantic import ConfigDict


def hidden_fields_config(*fields: str) -> ConfigDict:
    def _remove_fields(schema: dict) -> None:
        props = schema.get('properties', {})
        for field in fields:
            props.pop(field, None)
    return ConfigDict(json_schema_extra=_remove_fields)
