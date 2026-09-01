from fastapi import APIRouter

from applypilot.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=HealthResponse)
async def live() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/ready", response_model=HealthResponse)
async def ready() -> HealthResponse:
    # M1 scaffold readiness is intentionally non-sensitive. Database readiness
    # becomes authoritative when persistence models are implemented.
    return HealthResponse(status="ready")
