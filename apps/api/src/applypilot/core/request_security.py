from urllib.parse import urlsplit

from fastapi import Request

from applypilot.core.config import get_settings

PRIVATE_PROXY_HOST = "api:8000"


def browser_host_matches(request: Request) -> bool:
    expected = urlsplit(get_settings().allowed_origin).netloc
    host = request.headers.get("host")
    if host == expected:
        return True
    return host == PRIVATE_PROXY_HOST and request.headers.get("x-forwarded-host") == expected
