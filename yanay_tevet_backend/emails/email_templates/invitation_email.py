from pydantic import BaseModel

from emails.base_email import BaseEmail


class InvitationEmailContext(BaseModel):
    inviter_name: str = ''
    invitation_message: str = ''


class InvitationEmail(BaseEmail[InvitationEmailContext]):
    def get_template_name(self) -> str:
        return 'invitation_email'

    def get_subject(self) -> str:
        return "You've been invited to Yanay Tevet"
