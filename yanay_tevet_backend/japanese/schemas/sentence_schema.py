from ninja import Schema


class SentenceSchema(Schema):
    japanese: str
    english_translation: str
