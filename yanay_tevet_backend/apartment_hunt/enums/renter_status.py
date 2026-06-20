from common.base_enum import BaseEnum


class RenterStatus(BaseEnum):
    CONTACTED = 'contacted'
    SCHEDULED_TO_SEE = 'scheduled_to_see'
    VISITED = 'visited'
    DECLINED = 'declined'
    WANT_TO_SIGN = 'want_to_sign'
    SIGNED = 'signed'
