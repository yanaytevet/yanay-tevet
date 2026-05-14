from pydantic import BaseModel


class TableHeaderSchema(BaseModel):
    title: str
    key: str