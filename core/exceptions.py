import attr
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import (
    set_rollback,
    exception_handler as drf_exception_handler,
)


@attr.s(auto_attribs=True, auto_exc=True)
class BaseAPIException(Exception):
    """
    Base exception for API errors. (will be converted to DRF APIException)
    Attributes:
        code: A short error code.
        message: A human-readable error message.
        status_code: HTTP status code associated with the error.
    """

    code: str
    message: str
    status_code: int


def exception_handler(exc: Exception, context: dict) -> Response | None:
    response = None

    if isinstance(exc, ObjectDoesNotExist):
        exc = NotFound(str(exc))
    if isinstance(exc, BaseAPIException):
        data = attr.asdict(
            exc,
            filter=lambda attr, value: attr.name != 'status_code',
        )
        set_rollback()
        response = Response(data, status=exc.status_code)

    if response is None:
        response = drf_exception_handler(exc, context)
    return response
