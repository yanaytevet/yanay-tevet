from typing import TypedDict


class JwtTokenPayload(TypedDict):
    user_id: int
    type: str  # "access" or "refresh"
    exp: int
    iat: int