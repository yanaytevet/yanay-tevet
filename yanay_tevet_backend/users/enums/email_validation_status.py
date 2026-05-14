from common.base_enum import BaseEnum


class EmailValidationStatus(BaseEnum):
    NOT_CHECKED = 'not_checked'
    VALID = 'valid'
    INVALID = 'invalid'
    CATCH_ALL = 'catch_all'
    UNKNOWN = 'unknown'
