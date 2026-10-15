"""Translate course traffic requests to the original local chat API."""
import ipaddress
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

# Set only after real HTTP single-request validation.
ADAPTER_READY = True


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def local_base(base_url):
    parts = urlsplit(base_url)
    if (parts.scheme not in ('http', 'https') or not parts.hostname
            or parts.username or parts.password or parts.query or parts.fragment
            or parts.path not in ('', '/')):
        raise ValueError('Expected a local HTTP service root without credentials')
    host = parts.hostname.lower()
    if host != 'localhost':
        try:
            allowed = ipaddress.ip_address(host).is_loopback
        except ValueError:
            allowed = False
        if not allowed:
            raise ValueError('Only loopback addresses are allowed')
    return base_url.rstrip('/')


def confirm_mock_mode(base_url: str, timeout: float) -> bool:
    """Read actual server configuration over HTTP, refusing redirects."""
    base = local_base(base_url)
    opener = build_opener(ProxyHandler({}), NoRedirect())
    try:
        with opener.open(Request(base + '/api/lab-status', method='GET'), timeout=timeout) as response:
            if response.status != 200:
                return False
            data = json.loads(response.read(65536))
        return (isinstance(data, dict) and data.get('mode') == 'mock'
                and data.get('external_model_calls') is False)
    except (HTTPError, URLError, OSError, ValueError):
        return False


def build_chat_request(
    base_url: str, message: str, delay_seconds: float, force_error: bool
) -> Request:
    """Use the unchanged chat endpoint; mock settings run on the backend."""
    base = local_base(base_url)
    payload = {'message': message, 'mock': {
        'delay_seconds': delay_seconds, 'force_error': force_error,
    }}
    return Request(base + '/api/messages', data=json.dumps(payload).encode('utf-8'),
                   headers={'Content-Type': 'application/json'}, method='POST')


def response_is_success(status_code: int, body: bytes) -> bool:
    """A successful creation must contain a valid chat record, without error."""
    if status_code != 201:
        return False
    try:
        data = json.loads(body)
    except (ValueError, UnicodeError):
        return False
    return (isinstance(data, dict) and 'error' not in data
            and type(data.get('id')) is int and data['id'] > 0
            and isinstance(data.get('message'), str) and bool(data['message'].strip())
            and isinstance(data.get('reply'), str) and bool(data['reply'].strip()))
