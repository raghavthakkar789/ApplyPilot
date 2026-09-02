from collections.abc import Awaitable, Callable

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from applypilot.domain.documents.document_limits import LIMITS

UPLOAD_REQUEST_OVERHEAD_BYTES = 64 * 1024


async def enforce_resume_request_size(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    is_upload = request.method == "POST" and (
        request.url.path == "/api/resumes"
        or (request.url.path.startswith("/api/resumes/") and request.url.path.endswith("/versions"))
    )
    if is_upload:
        raw_length = request.headers.get("content-length")
        if raw_length is None or not raw_length.isdigit():
            return JSONResponse(
                status_code=411, content={"detail": "A valid request size is required."}
            )
        if int(raw_length) > LIMITS.upload_bytes + UPLOAD_REQUEST_OVERHEAD_BYTES:
            return JSONResponse(
                status_code=413, content={"detail": "The upload exceeds the 10 MiB limit."}
            )
    return await call_next(request)
