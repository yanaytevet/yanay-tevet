from ninja import Schema


class PassageSchema(Schema):
    title: str
    source: str = ''
    # The raw Japanese text of the whole passage. This is the source of truth for
    # ordering — the sentence nodes linked off a passage are unordered, so the
    # reading order lives here (and in the generated content_html).
    full_text: str
