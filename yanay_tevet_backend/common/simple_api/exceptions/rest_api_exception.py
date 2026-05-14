from ninja.errors import HttpError

from common.simple_api.enums.status_code import StatusCode


class RestAPIException(HttpError):
    def __init__(self, status_code: StatusCode, error_code: str, message: str):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
