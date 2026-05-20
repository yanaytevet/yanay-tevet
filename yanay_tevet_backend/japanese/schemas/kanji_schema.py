from ninja import Schema


class KanjiSchema(Schema):
    character: str
    readings_on: list[str]
    readings_kun: list[str]
    meanings: list[str]
    radicals: list[str]
