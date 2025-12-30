"""Middleware package for security and request handling."""
from app.middleware.rate_limiter import (
    limiter,
    setup_rate_limiter,
    AUTH_RATE_LIMIT,
    OTP_REQUEST_LIMIT,
    OTP_VERIFY_LIMIT,
    ADMIN_RATE_LIMIT,
    API_RATE_LIMIT,
    get_client_ip,
)

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
