from ninja import Schema


class GenerateContentInputSchema(Schema):
    user_note: str | None = None
