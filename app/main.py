"""Main FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from pathlib import Path

from app.config import settings
from app.database import engine, Base
from app.logging_config import setup_logging, get_logger, ExceptionLogger
from app.middleware.rate_limiter import setup_rate_limiter, limiter
from app.auth.routes import router as auth_router
from app.customers.routes import router as customers_router
from app.surveys.routes import router as surveys_router
from app.surveys.incomplete_routes import router as incomplete_surveys_router
from app.surveys.dynamic_routes import router as dynamic_questions_router
from app.companies.routes import router as companies_router
from app.companies.question_routes import router as company_questions_router
from app.companies.url_config_routes import router as url_config_router
from app.companies.details_routes import router as companies_details_router
from app.reports.routes import router as reports_router
from app.localization.routes import router as localization_router
from app.admin.question_variation_routes import router as admin_question_variation_router
from app.admin.variation_set_routes import router as admin_variation_set_router
from app.admin.demographic_rule_routes import router as admin_demographic_rule_router
from app.admin.localization_routes import router as admin_localization_router
from app.admin.localization_routes import router as admin_localization_router
from app.admin.simple_routes import simple_admin_router
from app.admin.email_automation_routes import router as email_automation_router
from app.surveys.financial_clinic_routes import router as financial_clinic_router
from debug_companies import router as debug_router
from app.consent.routes import router as consent_router
from app.consultations.routes import router as consultations_router
from app.crm.routes import router as crm_router

# Initialize centralized logging
setup_logging()
logger = get_logger(__name__)
exception_logger = ExceptionLogger(logger)

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

# =============================================================================
# Security Headers Middleware
# =============================================================================
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    Implements recommendations from security audit.
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # X-Frame-Options: Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-Content-Type-Options: Prevent MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-XSS-Protection: Enable XSS filtering (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer-Policy: Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions-Policy: Restrict browser features
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content-Security-Policy: Restrict content sources
        # Note: This is a strict policy - adjust based on application needs
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Required for some frameworks
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self' https:",
            "frame-ancestors 'none'",  # Equivalent to X-Frame-Options: DENY
            "base-uri 'self'",
            "form-action 'self'",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        # Strict-Transport-Security: Force HTTPS (only in production)
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Cache-Control for sensitive endpoints
        if "/auth/" in request.url.path or "/admin/" in request.url.path:
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        return response


# Add Security Headers Middleware (added first so it runs last)
app.add_middleware(SecurityHeadersMiddleware)

# =============================================================================
# Host Header Validation Middleware (Security Audit Requirement)
# =============================================================================
class HostHeaderValidationMiddleware(BaseHTTPMiddleware):
    """
    Explicit Host Header validation middleware.
    Prevents Host Header Injection attacks by validating the Host header.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip validation in development/debug mode
        if settings.DEBUG:
            return await call_next(request)
        
        # Get the host header
        host = request.headers.get("host", "").lower().split(":")[0]  # Remove port if present
        
        # Define allowed hosts (production only)
        allowed_hosts = [
            "localhost",
            "127.0.0.1",
            "uae-financial-health-filters-68ab0c8434cb.herokuapp.com",
            "financialclinic.ae",
            "www.financialclinic.ae",
        ]
        
        # Check if host is allowed (also allow subdomains of allowed domains)
        is_allowed = False
        for allowed_host in allowed_hosts:
            if allowed_host.startswith("."):
                # Wildcard subdomain match
                if host.endswith(allowed_host) or host == allowed_host[1:]:
                    is_allowed = True
                    break
            elif host == allowed_host or host.endswith(f".{allowed_host}"):
                is_allowed = True
                break
            # Also check for herokuapp.com and netlify.app patterns
            elif allowed_host in ["uae-financial-health-filters-68ab0c8434cb.herokuapp.com"]:
                if host.endswith(".herokuapp.com") or host == allowed_host:
                    is_allowed = True
                    break
        
        if not is_allowed:
            logger.warning(f"Host header validation failed: {host}")
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid host header"}
            )
        
        return await call_next(request)

app.add_middleware(HostHeaderValidationMiddleware)

# Configure CORS FIRST - This must be before other middleware
origins = settings.allowed_origins
print(f"🔧 [DEBUG] CORS Origins: {origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Keep ProxyHeaders - it's not the issue
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# Now test TrustedHost middleware - this is likely the culprit
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts_list if not settings.DEBUG else ["*"]
)

# Initialize Rate Limiter (must be done during app initialization, not startup)
setup_rate_limiter(app)


# Custom middleware for request logging and timing
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log requests and response times."""
    start_time = time.time()
    
    # Log request (handle None client in test environment)
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"{request.method} {request.url.path} - {client_host}")
    
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
    """Handle unexpected exceptions gracefully and log them."""
    # Log the exception with full context
    exception_logger.log_request_error(
        request_path=str(request.url.path),
        method=request.method,
        exc=exc,
        extra_data={
            "query_params": str(request.query_params),
            "client_host": request.client.host if request.client else "unknown"
        }
    )
    
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
app.include_router(companies_details_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(localization_router, prefix="/api/v1")
app.include_router(consent_router, prefix="/api/v1")  # PDPL-compliant consent management
app.include_router(admin_question_variation_router, prefix="/api/v1")
app.include_router(admin_variation_set_router, prefix="/api/v1")
app.include_router(admin_demographic_rule_router, prefix="/api/v1")
app.include_router(admin_localization_router, prefix="/api/v1")
app.include_router(simple_admin_router, prefix="/api/v1")
app.include_router(email_automation_router, prefix="/api/v1/admin")
app.include_router(crm_router, prefix="/api/v1")
app.include_router(debug_router, prefix="/api/v1")  # Debug endpoint
from app.admin import variation_routes
app.include_router(variation_routes.router, prefix="/api/v1")

# Mount static files for serving assets in emails and PDFs
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"✅ Static files mounted at /static from {static_dir}")
else:
    logger.warning(f"⚠️ Static directory not found at {static_dir}")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    logger.info("Starting UAE Financial Health Check API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info("✅ Rate limiter already initialized during app setup")
    
    # Initialize APScheduler
    try:
        # Check security settings in production
        if settings.ENVIRONMENT == "production" and not settings.SECRET_KEY:
            logger.critical("❌ CRITICAL SECURITY ERROR: SECRET_KEY not set in production!")
            raise ValueError("SECRET_KEY must be set in production environment")
            
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
