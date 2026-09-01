from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from applypilot.api.router import api_router
from applypilot.core.config import get_settings
from applypilot.core.logging import configure_logging
from applypilot.schemas.errors import ErrorDetail, ErrorResponse


def create_application() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    application = FastAPI(title=settings.api_title, version=settings.api_version)
    application.include_router(api_router)

    @application.exception_handler(Exception)
    async def unhandled_error(_request: Request, _error: Exception) -> JSONResponse:
        payload = ErrorResponse(
            error=ErrorDetail(code="internal_error", message="The request could not be completed.")
        )
        return JSONResponse(status_code=500, content=payload.model_dump())

    return application


app = create_application()
