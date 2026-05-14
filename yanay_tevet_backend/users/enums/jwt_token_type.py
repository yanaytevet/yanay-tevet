from common.base_enum import BaseEnum


class JwtTokenType(BaseEnum):
    ACCESS = 'access'
    REFRESH = 'refresh'
