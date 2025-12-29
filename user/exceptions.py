import attr

from core.exceptions import BaseAPIException


@attr.s(auto_attribs=True, auto_exc=True)
class ClientNotFound(BaseAPIException):
    code: str = 'client_not_found'
    message: str = 'The specified client does not exist.'
    status_code: int = 404


@attr.s(auto_attribs=True, auto_exc=True)
class MissingInstallIdHeader(BaseAPIException):
    code: str = 'missing_install_id_header'
    message: str = 'X-Install-Id header is required.'
    status_code: int = 400
