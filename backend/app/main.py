from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.upload import router as upload_router
from app.api.parse import router as parse_router
from app.api.extract import router as extract_router
from app.verification import ComparisonRegistry, verify_router
from app.readiness.api.readiness import router as readiness_router
from app.config import settings
from app.extractors.specification_registry import SpecificationRegistry
from app.extractors.template_loader import TemplateLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Duelens API",
    description="Backend for Duelens fundraising document consistency verification.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from app.core import request_id_var

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_var.set(req_id)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = req_id
            return response
        finally:
            request_id_var.reset(token)

app.add_middleware(RequestIdMiddleware)

from app.core import setup_logging, validate_startup_state
setup_logging()

# Application Startup Lifecycle Phase
@app.on_event("startup")
async def startup_event():
    validate_startup_state()

# Include Routers
app.include_router(upload_router, prefix="/api/v1/upload", tags=["Upload"])
app.include_router(parse_router, prefix="/api/v1/parse", tags=["Parse"])
app.include_router(extract_router, prefix="/api/v1/extract", tags=["Extract"])
app.include_router(verify_router, prefix="/api/v1/verify", tags=["Verify"])
app.include_router(readiness_router, prefix="/api/v1/readiness", tags=["Readiness"])

from app.api.pipeline import router as pipeline_router
from app.api.companies import router as companies_router
from app.api.artifacts import router as artifacts_router

app.include_router(pipeline_router, prefix="/api/v1/pipeline", tags=["Pipeline"])
app.include_router(companies_router, prefix="/api/v1/companies", tags=["Companies"])
app.include_router(artifacts_router, prefix="/api/v1", tags=["Artifacts"])

@app.get("/")
async def root():
    return {
        "app": "Duelens API",
        "status": "healthy",
        "version": "1.0.0"
    }
