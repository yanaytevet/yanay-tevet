import traceback

from django.contrib.auth import get_user
from django.http import HttpRequest


class ExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request: HttpRequest, exception):
        exc_tb = traceback.format_exc()
        msg = f'{request.get_full_path()}-{exception}'
        user = get_user(request)
        full_msg = f'by {user}\n{exc_tb}'
        # AdminEmailsManager().send_error_to_rnd_admins(msg, full_msg)
        return None
