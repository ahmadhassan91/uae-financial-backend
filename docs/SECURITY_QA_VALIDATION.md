# Security Implementation QA Validation Guidelines

This document provides step-by-step validation guidelines for QA to test and validate the security implementations based on the security audit recommendations.

---

## Table of Contents

1. [HTTP Security Headers](#1-http-security-headers)
2. [Rate Limiting](#2-rate-limiting)
3. [OTP Security & Account Lockout](#3-otp-security--account-lockout)
4. [Host Header Validation](#4-host-header-validation)
5. [Progressive Delays](#5-progressive-delays)
6. [Security Logging](#6-security-logging)

---

## 1. HTTP Security Headers

### 1.1 Test Setup
- Use browser developer tools (Network tab) or tools like `curl` to inspect response headers
- Test in both development and production environments

### 1.2 Validation Steps

#### Test 1.2.1: X-Frame-Options Header
**Purpose:** Prevent clickjacking attacks

```bash
curl -I https://your-api-domain.com/api/v1/health
```

**Expected Result:**
```
X-Frame-Options: DENY
```

**Manual Browser Test:**
1. Try to embed the application in an iframe on another domain
2. The page should NOT load in the iframe

---

#### Test 1.2.2: X-Content-Type-Options Header
**Purpose:** Prevent MIME-type sniffing

```bash
curl -I https://your-api-domain.com/api/v1/health
```

**Expected Result:**
```
X-Content-Type-Options: nosniff
```

---

#### Test 1.2.3: Content-Security-Policy Header
**Purpose:** Restrict content sources to prevent XSS

```bash
curl -I https://your-api-domain.com/api/v1/health
```

**Expected Result:**
```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:; frame-ancestors 'none'; base-uri 'self'; form-action 'self'
```

---

#### Test 1.2.4: Strict-Transport-Security (HSTS) Header
**Purpose:** Force HTTPS connections (production only)

```bash
curl -I https://your-production-domain.com/api/v1/health
```

**Expected Result (Production Only):**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

**Note:** This header should NOT appear in development/local environments.

---

#### Test 1.2.5: Referrer-Policy Header
**Purpose:** Control referrer information leakage

```bash
curl -I https://your-api-domain.com/api/v1/health
```

**Expected Result:**
```
Referrer-Policy: strict-origin-when-cross-origin
```

---

#### Test 1.2.6: Cache-Control for Sensitive Endpoints
**Purpose:** Prevent caching of sensitive data

```bash
curl -I https://your-api-domain.com/api/v1/auth/me
```

**Expected Result for /auth/* and /admin/* endpoints:**
```
Cache-Control: no-store, no-cache, must-revalidate, private
Pragma: no-cache
Expires: 0
```

---

## 2. Rate Limiting

### 2.1 Test Setup
- Use tools like `curl`, Postman, or custom scripts
- Clear any existing rate limit counters between tests

### 2.2 Validation Steps

#### Test 2.2.1: OTP Request Rate Limiting (5 requests/minute)
**Purpose:** Prevent OTP spam attacks

**Steps:**
1. Send 5 OTP requests in quick succession to the same email:
```bash
for i in {1..6}; do
  curl -X POST https://your-api-domain.com/api/v1/auth/otp/request \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "language": "en"}'
  echo "Request $i completed"
done
```

**Expected Results:**
- Requests 1-5: Should succeed (HTTP 200) or return email-based rate limit message
- Request 6+: Should return HTTP 429 Too Many Requests

**Expected Response for Rate Limited Request:**
```json
{
  "error": "Too Many Requests",
  "detail": "Rate limit exceeded. Please slow down and try again later."
}
```

---

#### Test 2.2.2: OTP Verify Rate Limiting (10 requests/minute)
**Purpose:** Prevent OTP brute-force attacks

**Steps:**
1. Send 11 OTP verification requests in quick succession:
```bash
for i in {1..11}; do
  curl -X POST https://your-api-domain.com/api/v1/auth/otp/verify \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "code": "123456"}'
  echo "Request $i completed"
done
```

**Expected Results:**
- Requests 1-10: Should process (may fail with invalid OTP, but not rate limited)
- Request 11+: Should return HTTP 429 Too Many Requests

---

#### Test 2.2.3: General API Rate Limiting (200 requests/minute)
**Purpose:** Prevent API abuse

**Steps:**
1. Send 201 requests to a general endpoint:
```bash
for i in {1..201}; do
  curl -s -o /dev/null -w "%{http_code}\n" https://your-api-domain.com/api/v1/health
done | sort | uniq -c
```

**Expected Results:**
- First 200 requests: HTTP 200
- Request 201+: HTTP 429

---

## 3. OTP Security & Account Lockout

### 3.1 Test Setup
- Use a test email account
- Clear lockout records between tests

### 3.2 Validation Steps

#### Test 3.2.1: OTP Expiry (5 minutes)
**Purpose:** Ensure OTPs expire after 5 minutes

**Steps:**
1. Request an OTP for a test email
2. Note the OTP code (from email or database)
3. Wait 6 minutes
4. Try to verify the OTP

**Expected Result:**
```json
{
  "detail": "OTP code has expired. Please request a new one."
}
```

---

#### Test 3.2.2: OTP Max Attempts (3 per OTP)
**Purpose:** Prevent brute-forcing a single OTP

**Steps:**
1. Request an OTP
2. Try to verify with wrong codes 3 times
3. Try to verify with the correct code on the 4th attempt

**Expected Result after 3 wrong attempts:**
```json
{
  "detail": "Too many verification attempts. Please request a new OTP."
}
```

---

#### Test 3.2.3: Account Lockout (5 failed attempts)
**Purpose:** Lock account after repeated failures

**Steps:**
1. Request an OTP for a test email
2. Try to verify with wrong codes 5 times (different OTPs or codes)
3. Try to verify again (even with correct code)

**Expected Result after 5 failures:**
```json
{
  "detail": "Too many failed attempts. Account locked for 15 minutes."
}
```

**HTTP Status Code:** 429 Too Many Requests

---

#### Test 3.2.4: Account Lockout Duration
**Purpose:** Verify lockout duration is correct

**Steps:**
1. Trigger account lockout (5 failed attempts)
2. Wait 15 minutes
3. Try to verify OTP again

**Expected Result:**
- After lockout expires, verification should be allowed again

---

#### Test 3.2.5: Successful Login Resets Lockout Counter
**Purpose:** Verify successful login clears failed attempts

**Steps:**
1. Make 3 failed OTP verification attempts
2. Successfully verify a valid OTP
3. Make 3 more failed attempts

**Expected Result:**
- Should NOT be locked out after step 3 (counter was reset)

---

#### Test 3.2.6: OTP Code Format Validation
**Purpose:** Ensure only 6-digit codes are accepted

**Steps:**
1. Try to verify with invalid formats:
   - `12345` (5 digits)
   - `1234567` (7 digits)
   - `abcdef` (letters)
   - `12-34-56` (with dashes)

**Expected Result:**
```json
{
  "detail": "Invalid code format. Code must be 6 digits."
}
```

---

## 4. Host Header Validation

### 4.1 Test Setup
- Use `curl` with custom Host headers

### 4.2 Validation Steps

#### Test 4.2.1: Valid Host Header
**Purpose:** Ensure valid hosts are accepted

```bash
curl -H "Host: your-api-domain.herokuapp.com" \
  https://your-api-domain.herokuapp.com/api/v1/health
```

**Expected Result:** HTTP 200 OK

---

#### Test 4.2.2: Invalid Host Header (Production)
**Purpose:** Ensure invalid hosts are rejected

```bash
curl -H "Host: evil-domain.com" \
  https://your-api-domain.herokuapp.com/api/v1/health
```

**Expected Result:** HTTP 400 Bad Request (Invalid host header)

**Note:** This test may behave differently in development mode where all hosts are allowed.

---

## 5. Progressive Delays

### 5.1 Test Setup
- Use timing tools to measure response times

### 5.2 Validation Steps

#### Test 5.2.1: Progressive Delay After Failed Attempts
**Purpose:** Verify delays increase with failed attempts

**Steps:**
1. Make consecutive failed OTP verification attempts and measure response times

**Expected Delays (approximate):**
| Attempt | Expected Delay |
|---------|----------------|
| 1       | 0 seconds      |
| 2       | 2 seconds      |
| 3       | 4 seconds      |
| 4       | 8 seconds      |
| 5       | 16 seconds     |
| 6+      | 30 seconds (capped) |

**Note:** The account may lock before reaching higher delays.

---

## 6. Security Logging

### 6.1 Test Setup
- Access to application logs (Heroku logs, CloudWatch, etc.)
- Database access for audit_logs table

### 6.2 Validation Steps

#### Test 6.2.1: Failed OTP Verification Logging
**Purpose:** Verify failed attempts are logged

**Steps:**
1. Make a failed OTP verification attempt
2. Check audit_logs table

**Expected Log Entry:**
```sql
SELECT * FROM audit_logs 
WHERE action = 'otp_verification_failed' 
ORDER BY created_at DESC LIMIT 1;
```

**Expected Fields:**
- `action`: "otp_verification_failed"
- `entity_type`: "otp"
- `details`: Contains email, reason, is_locked, remaining_attempts
- `ip_address`: Client IP
- `user_agent`: Client user agent

---

#### Test 6.2.2: Account Lockout Logging
**Purpose:** Verify account lockouts are logged

**Steps:**
1. Trigger an account lockout (5 failed attempts)
2. Check audit_logs table

**Expected Log Entry:**
```sql
SELECT * FROM audit_logs 
WHERE action = 'account_locked' 
ORDER BY created_at DESC LIMIT 1;
```

**Expected Fields:**
- `action`: "account_locked"
- `entity_type`: "security"
- `details`: Contains identifier, attempt_count, lockout_minutes

---

#### Test 6.2.3: Rate Limit Exceeded Logging
**Purpose:** Verify rate limit violations are logged

**Steps:**
1. Trigger a rate limit (exceed request limit)
2. Check application logs

**Expected Log Entry:**
```
WARNING - Rate limit exceeded - IP: x.x.x.x, Path: /api/v1/auth/otp/request, Limit: 5/minute
```

---

## Quick Validation Checklist

Use this checklist to quickly verify all security implementations:

### Security Headers
- [ ] X-Frame-Options: DENY present
- [ ] X-Content-Type-Options: nosniff present
- [ ] Content-Security-Policy present
- [ ] Strict-Transport-Security present (production only)
- [ ] Referrer-Policy present
- [ ] Cache-Control headers on auth/admin endpoints

### Rate Limiting
- [ ] OTP request limited to 5/minute
- [ ] OTP verify limited to 10/minute
- [ ] General API limited to 200/minute
- [ ] 429 response returned when exceeded

### OTP Security
- [ ] OTP expires after 5 minutes
- [ ] Max 3 attempts per OTP
- [ ] 6-digit format validation works

### Account Lockout
- [ ] Account locks after 5 failed attempts
- [ ] Lockout duration is 15 minutes
- [ ] Successful login resets counter
- [ ] 429 response when locked

### Host Validation
- [ ] Valid hosts accepted
- [ ] Invalid hosts rejected (production)

### Logging
- [ ] Failed OTP attempts logged
- [ ] Account lockouts logged
- [ ] Rate limit violations logged

---

## Testing Tools Recommendations

1. **curl** - Command-line HTTP requests
2. **Postman** - GUI-based API testing
3. **Burp Suite** - Security testing proxy
4. **OWASP ZAP** - Web security scanner
5. **k6** - Load testing for rate limits

---

## Notes for QA

1. **Test Environment:** Always test in a staging environment first before production
2. **Data Cleanup:** Clear test data and lockout records between test sessions
3. **Rate Limit Reset:** Rate limits reset after the time window (1 minute for most)
4. **Lockout Reset:** Account lockouts can be manually cleared in the database if needed:
   ```sql
   DELETE FROM failed_login_attempts WHERE identifier = 'test@example.com';
   ```

---

*Document Version: 1.0*
*Last Updated: December 2024*
*Security Audit Implementation*
