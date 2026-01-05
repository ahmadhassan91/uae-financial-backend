"""
Rate Limiting Middleware for API Security.

Implements IP-based and user-based rate limiting for sensitive endpoints.
Addresses security audit recommendations for brute-force protection.
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request
from typing import Callable
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# Rate Limiter Configuration
# =============================================================================

def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request, handling proxy headers.
    """
    # Check for forwarded headers (common with proxies/load balancers)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For can contain multiple IPs, first one is the client
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to direct client IP
    if request.client:
        return request.client.host
    
    return "unknown"


# Create limiter instance with custom key function
limiter = Limiter(
    key_func=get_client_ip,
    default_limits=["1000/minute"],  # Increased default limit for all endpoints
    storage_uri="memory://",  # Use in-memory storage (use Redis in production for distributed systems)
    strategy="fixed-window",
)

# =============================================================================
# Rate Limit Decorators for Different Endpoint Types
# =============================================================================

# Strict limits for authentication endpoints
AUTH_RATE_LIMIT = "10/minute"  # 10 requests per minute for auth

# Stricter limits for OTP endpoints
OTP_REQUEST_LIMIT = "5/minute"  # 5 OTP requests per minute
OTP_VERIFY_LIMIT = "10/minute"  # 10 OTP verifications per minute

# Admin endpoint limits
ADMIN_RATE_LIMIT = "100/minute"  # 100 requests per minute for admin

# General API limits
API_RATE_LIMIT = "200/minute"  # 200 requests per minute for general API
DEFAULT_RATE_LIMIT = "200/minute"  # Default rate limit for all endpoints


def get_rate_limit_key_user(request: Request) -> str:
    """
    Get rate limit key combining IP and user identifier for user-specific limits.
    """
    ip = get_client_ip(request)
    
    # Try to get user identifier from authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        # Use a hash of the token to identify the user
        token_hash = hash(auth_header[7:20])  # First 13 chars of token
        return f"{ip}:{token_hash}"
    
    return ip


# =============================================================================
# Rate Limit Response Handler
# =============================================================================

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for rate limit exceeded errors.
    Logs the event and returns a proper error response.
    """
    client_ip = get_client_ip(request)
    logger.warning(
        f"Rate limit exceeded - IP: {client_ip}, Path: {request.url.path}, "
        f"Limit: {exc.detail}"
    )
    
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Please slow down and try again later.",
            "retry_after": getattr(exc, 'retry_after', 60)
        },
        headers={
            "Retry-After": str(getattr(exc, 'retry_after', 60)),
            "X-RateLimit-Limit": str(exc.detail) if exc.detail else "unknown",
        }
    )


# =============================================================================
# Utility Functions
# =============================================================================

def setup_rate_limiter(app):
    """
    Setup rate limiter on FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    logger.info("✅ Rate limiter initialized successfully")


# Export commonly used decorators
__all__ = [
    'limiter',
    'setup_rate_limiter',
    'AUTH_RATE_LIMIT',
    'OTP_REQUEST_LIMIT',
    'OTP_VERIFY_LIMIT',
    'ADMIN_RATE_LIMIT',
    'API_RATE_LIMIT',
    'get_client_ip',
]
