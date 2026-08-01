from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.upload import router as upload_router
from app.api.parse import router as parse_router
from app.api.extract import router as extract_router
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

# Application Startup Lifecycle Phase
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Duelens Extraction Orchestration Engine...")
    try:
        SpecificationRegistry.load()
        TemplateLoader.warm_cache()
        logger.info("Specification Registry and Template Loader warmed successfully.")
    except Exception as e:
        logger.error(f"Error during application startup phase: {str(e)}")

# Include Routers
app.include_router(upload_router, prefix="/api/v1/upload", tags=["Upload"])
app.include_router(parse_router, prefix="/api/v1/parse", tags=["Parse"])
app.include_router(extract_router, prefix="/api/v1/extract", tags=["Extract"])

@app.get("/")
async def root():
    return {
        "app": "Duelens API",
        "status": "healthy",
        "version": "1.0.0"
    }
