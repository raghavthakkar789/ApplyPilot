from fastapi import APIRouter

from applypilot.api.health import router as health_router
from applypilot.api.routes.authentication import router as authentication_router
from applypilot.api.routes.candidate_fact_conflicts import router as candidate_fact_conflicts_router
from applypilot.api.routes.candidate_facts import router as candidate_facts_router
from applypilot.api.routes.initialization import router as initialization_router
from applypilot.api.routes.profile import router as profile_router
from applypilot.api.routes.resume_fact_candidates import router as resume_candidates_router
from applypilot.api.routes.resumes import router as resumes_router
from applypilot.api.routes.sessions import router as sessions_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(initialization_router)
api_router.include_router(authentication_router)
api_router.include_router(sessions_router)
api_router.include_router(profile_router)
api_router.include_router(candidate_facts_router)
api_router.include_router(candidate_fact_conflicts_router)
api_router.include_router(resumes_router)
api_router.include_router(resume_candidates_router)
