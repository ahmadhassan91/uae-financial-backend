"""Main FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from app.config import settings
from app.database import engine, Base
from app.auth.routes import router as auth_router
from app.customers.routes import router as customers_router
from app.surveys.routes import router as surveys_router
from app.surveys.incomplete_routes import router as incomplete_surveys_router
from app.surveys.dynamic_routes import router as dynamic_questions_router
from app.companies.routes import router as companies_router
from app.companies.question_routes import router as company_questions_router
from app.companies.url_config_routes import router as url_config_router
from app.reports.routes import router as reports_router
from app.localization.routes import router as localization_router
from app.admin.question_variation_routes import router as admin_question_variation_router
from app.admin.variation_set_routes import router as admin_variation_set_router
from app.admin.demographic_rule_routes import router as admin_demographic_rule_router
from app.admin.localization_routes import router as admin_localization_router
from app.admin.simple_routes import simple_admin_router
from app.surveys.financial_clinic_routes import router as financial_clinic_router
from app.consent.routes import router as consent_router
from app.consultations.routes import router as consultations_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="UAE Financial Health Check API",
    description="Backend API for the UAE Financial Health Check application",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None
)

# TrustedHostMiddleware removed - CORS middleware provides sufficient protection
# and the wildcard patterns weren't working correctly with Heroku's dynamic hostnames

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Custom middleware for request logging and timing
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log requests and response times."""
    start_time = time.time()
    
    # Log request
    logger.info(f"{request.method} {request.url.path} - {request.client.host}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate and log response time
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    
    # Add response time header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions gracefully."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": "An unexpected error occurred. Please try again later."
            }
        )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time()
    }


# API v1 Health check endpoint
@app.get("/api/v1/health")
async def api_v1_health_check():
    """API v1 health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time(),
        "api_version": "v1"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "UAE Financial Health Check API",
        "version": "1.0.0",
        "docs_url": "/docs" if settings.DEBUG else "Documentation not available in production",
        "health_check": "/health"
    }


# Include routers with /api/v1 prefix
app.include_router(auth_router, prefix="/api/v1")
app.include_router(customers_router, prefix="/api/v1")
app.include_router(surveys_router, prefix="/api/v1")
app.include_router(incomplete_surveys_router, prefix="/api/v1")
app.include_router(dynamic_questions_router, prefix="/api/v1")
app.include_router(financial_clinic_router, prefix="/api/v1")  # Financial Clinic survey system
app.include_router(consultations_router, prefix="/api/v1")  # Consultation requests
app.include_router(companies_router, prefix="/api/v1")
app.include_router(company_questions_router, prefix="/api/v1")
app.include_router(url_config_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(localization_router, prefix="/api/v1")
app.include_router(consent_router, prefix="/api/v1")  # PDPL-compliant consent management
app.include_router(admin_question_variation_router, prefix="/api/v1")
app.include_router(admin_variation_set_router, prefix="/api/v1")
app.include_router(admin_demographic_rule_router, prefix="/api/v1")
app.include_router(admin_localization_router, prefix="/api/v1")
app.include_router(simple_admin_router, prefix="/api/v1")
from app.admin import variation_routes
app.include_router(variation_routes.router, prefix="/api/v1")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    logger.info("Starting UAE Financial Health Check API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize APScheduler
    try:
        from app.scheduler_setup import init_scheduler
        init_scheduler()
        logger.info("✅ APScheduler initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize APScheduler: {e}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    logger.info("Shutting down UAE Financial Health Check API")
    
    # Shutdown APScheduler
    try:
        from app.scheduler_setup import shutdown_scheduler
        shutdown_scheduler()
        logger.info("✅ APScheduler shut down successfully")
    except Exception as e:
        logger.error(f"❌ Failed to shutdown APScheduler: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
