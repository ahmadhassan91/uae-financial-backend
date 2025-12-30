# Security Recommendations

## Critical Priority

### 1. Enforce SECRET_KEY in Production
**Issue**: The `SECRET_KEY` in `app/config.py` defaults to an empty string, which is insecure for JWT signing.

**Fix**: Add validation in `app/main.py` startup:
```python
@app.on_event("startup")
async def startup_event():
    if settings.ENVIRONMENT == "production" and not settings.SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in production environment")
```

### 2. Remove Hardcoded Admin Credentials
**Issue**: `scripts/admin/create_production_admin.py` contains hardcoded passwords (`admin123`, `viewonly123`).

**Fix**: Modify the script to:
- Read passwords from environment variables
- Prompt for passwords interactively
- Generate secure random passwords and display them once

**Example**:
```python
import secrets
import getpass

# Option 1: From environment
admin_password = os.getenv("ADMIN_PASSWORD") or getpass.getpass("Enter admin password: ")

# Option 2: Generate secure password
admin_password = secrets.token_urlsafe(16)
print(f"Generated admin password: {admin_password}")
print("SAVE THIS PASSWORD - it will not be shown again!")
```

### 3. Add Token Expiry for Public Report Links
**Issue**: Public PDF download links in `app/reports/routes.py` have no expiry mechanism.

**Recommendation**:
- Add a `ReportDownloadToken` table with `token`, `created_at`, `expires_at`, `used_at`
- Validate tokens against this table in `download_public_report()`
- Set expiry to 7-30 days
- Mark tokens as used after first download (optional)

## High Priority

### 4. Migrate to HttpOnly Cookies for JWT
**Issue**: JWTs stored in `localStorage` are vulnerable to XSS attacks.

**Recommendation**:
- Use `httpOnly`, `secure`, `sameSite` cookies for tokens
- Update backend to set cookies in login responses
- Update frontend to remove localStorage token management
- Requires CORS configuration updates

### 5. Add Content Security Policy (CSP)
**Issue**: No CSP headers in Next.js application.

**Fix**: Add to `next.config.ts`:
```typescript
async headers() {
  return [
    {
      source: '/:path*',
      headers: [
        {
          key: 'Content-Security-Policy',
          value: [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'", // Adjust as needed
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self' https://your-api-domain.com",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
          ].join('; ')
        },
        {
          key: 'X-Frame-Options',
          value: 'DENY'
        },
        {
          key: 'X-Content-Type-Options',
          value: 'nosniff'
        },
        {
          key: 'Referrer-Policy',
          value: 'strict-origin-when-cross-origin'
        }
      ]
    }
  ];
}
```

### 6. Reintroduce TrustedHostMiddleware
**Issue**: TrustedHostMiddleware was removed; CORS alone doesn't prevent host header attacks.

**Fix**: Add back to `app/main.py`:
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts_list
)
```

### 7. Restrict CORS Origins in Production
**Issue**: CORS configuration may be too permissive.

**Recommendation**:
- Use explicit domain list in production
- Avoid wildcards
- Set `CORS_ORIGINS` environment variable to specific domains only

## Medium Priority

### 8. Add Rate Limiting Middleware
**Recommendation**: Add rate limiting for all API endpoints, not just OTP.

**Example using slowapi**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/login")
@limiter.limit("5/minute")
async def login_user(...):
    ...
```

### 9. Add Input Validation and Sanitization
**Recommendation**:
- Use Pydantic models for all request validation
- Add length limits on string fields
- Validate email formats strictly
- Sanitize file paths in download endpoints

### 10. Implement Audit Logging for Sensitive Operations
**Status**: Partially implemented

**Recommendation**:
- Ensure all admin actions are logged
- Log failed authentication attempts
- Log data exports and bulk operations
- Consider centralized logging (e.g., CloudWatch, Datadog)

### 11. Add HTTPS Enforcement
**Recommendation**: For production deployment:
- Enforce HTTPS at load balancer/reverse proxy level
- Set `secure=True` for cookies
- Add HSTS header: `Strict-Transport-Security: max-age=31536000; includeSubDomains`

### 12. Implement Password Complexity Requirements
**Current**: No password complexity validation

**Recommendation**: Add to registration/password change:
```python
import re

def validate_password_strength(password: str) -> bool:
    if len(password) < 12:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True
```

## Low Priority

### 13. Add Security Headers to API Responses
**Recommendation**: Add middleware to set security headers on all responses:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`

### 14. Implement Session Timeout
**Current**: JWT expiry is set, but no idle timeout

**Recommendation**:
- Track last activity time
- Invalidate sessions after 30 minutes of inactivity
- Requires session storage (Redis)

### 15. Add Dependency Scanning
**Recommendation**:
- Use `safety` for Python: `safety check`
- Use `npm audit` for Node.js
- Integrate into CI/CD pipeline
- Set up automated dependency updates (Dependabot)

## Code Quality Improvements

### 16. Split Large Files
**Issue**: `app/reports/email_service.py` is 1792 lines

**Recommendation**:
- Split into `email_templates.py`, `email_delivery.py`, `storage_service.py`
- Improve maintainability and testability

### 17. Add Type Hints
**Status**: Partially implemented

**Recommendation**:
- Add type hints to all function signatures
- Use `mypy` for static type checking
- Configure `mypy.ini` with strict mode

### 18. Add Comprehensive Tests
**Recommendation**:
- Unit tests for all business logic
- Integration tests for API endpoints
- Security tests for authentication flows
- Aim for >80% code coverage

## Deployment Checklist

Before deploying to production:

- [ ] Set `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False`
- [ ] Configure `CORS_ORIGINS` with explicit domains
- [ ] Set `ALLOWED_HOSTS` with production domains
- [ ] Enable HTTPS and set `secure` cookies
- [ ] Configure proper SMTP credentials
- [ ] Set up database backups
- [ ] Configure monitoring and alerting
- [ ] Review and rotate all API keys and secrets
- [ ] Test authentication flows thoroughly
- [ ] Verify rate limiting is active
- [ ] Check CSP headers are set correctly
- [ ] Ensure error messages don't leak sensitive info
- [ ] Review audit logs configuration
- [ ] Test disaster recovery procedures

## Monitoring Recommendations

1. **Application Monitoring**:
   - Track failed login attempts
   - Monitor API error rates
   - Alert on unusual traffic patterns

2. **Security Monitoring**:
   - Log and alert on privilege escalations
   - Monitor for SQL injection attempts
   - Track file access patterns

3. **Performance Monitoring**:
   - Database query performance
   - API response times
   - Memory and CPU usage

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [Next.js Security Headers](https://nextjs.org/docs/advanced-features/security-headers)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
