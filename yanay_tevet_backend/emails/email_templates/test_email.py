from pydantic import BaseModel

from emails.base_email import BaseEmail


class TestEmailContext(BaseModel):
    message: str = ''


class TestEmail(BaseEmail[TestEmailContext]):
    def get_template_name(self) -> str:
        return 'test_email'

    def get_subject(self) -> str:
        return 'Test Email — Yanay Tevet'
