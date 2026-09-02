from fastapi import APIRouter

from applypilot.api.health import router as health_router
from applypilot.api.routes.authentication import router as authentication_router
from applypilot.api.routes.initialization import router as initialization_router
from applypilot.api.routes.sessions import router as sessions_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(initialization_router)
api_router.include_router(authentication_router)
api_router.include_router(sessions_router)
