from common.base_enum import BaseEnum


class ProspectStatus(BaseEnum):
    SAW = 'saw'
    CONTACTED = 'contacted'
    WAITING_FOR_INVITATION = 'waiting_for_invitation'
    SAW_WAITING_FOR_THEM = 'saw_waiting_for_them'
    NEED_TO_DECIDE = 'need_to_decide'
    DECLINED = 'declined'
    ACCEPTED = 'accepted'
    SIGNED = 'signed'
