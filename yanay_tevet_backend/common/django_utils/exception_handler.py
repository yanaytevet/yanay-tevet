from django.http import HttpRequest, HttpResponse
from ninja.errors import ValidationError
from ninja.renderers import JSONRenderer


def custom_exception_handler(request: HttpRequest, exc: Exception) -> HttpResponse | None:
    if isinstance(exc, ValidationError):
        # Print full details of the validation error
        print("Validation Error:", exc.errors)
        body = JSONRenderer().render(request, {
            "detail": "Validation Error",
            "errors": exc.errors,  # Includes location, message, and type
        }, response_status=422)
        return HttpResponse(body, content_type="application/json", status=422)
    return None
