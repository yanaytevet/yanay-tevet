from ninja import Schema

from japanese.enums.word_sub_type import WordSubType
from japanese.enums.word_type import WordType


class WordSchema(Schema):
    base_form: str
    reading: str
    word_type: WordType
    word_sub_type: WordSubType | None = None
    meanings: list[str]
