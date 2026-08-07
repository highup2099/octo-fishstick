# Security Implementation Guide

This document describes the security measures implemented to address identified vulnerabilities.

## 1. JWT Authentication & Authorization ✅

### Implementation
- **File**: `apps/api/app/core/security.py`
- JWT tokens are used for all authenticated endpoints
- Token validation includes:
  - Signature verification using `jwt_secret`
  - Expiration check
  - Subject (user_id) validation

### Usage
All API endpoints now require Bearer token authentication:
```bash
curl -H "Authorization: Bearer <your_jwt_token>" http://localhost:8000/api/v1/quotes
```

### Token Generation
```python
from app.core.security import create_access_token
from uuid import UUID

token = create_access_token(
    user_id=UUID("your-user-uuid"),
    username="optional_username",
    expires_delta=timedelta(minutes=30)
)
```

## 2. Database Credentials Management ✅

### Changes
- **File**: `docker-compose.yml`
- Removed hardcoded credentials
- All sensitive values now use environment variables
- Application validates that default credentials are not used

### Setup
1. Copy `.env.example` to `.env`
2. Generate secure passwords:
   ```bash
   # Generate secure password
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # Generate JWT secret (min 32 chars)
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
3. Update `.env` with your secure values

### Validation
The application will fail to start if:
- `POSTGRES_PASSWORD` is not set
- `JWT_SECRET` is less than 32 characters
- `DATABASE_URL` contains default 'broker:broker' credentials

## 3. CORS Configuration ✅

### File: `apps/api/app/main.py`

#### Development Mode
- Allowed origins: `http://localhost:3000`, `http://localhost:3001`
- Explicit methods: GET, POST, PUT, DELETE, PATCH
- Explicit headers: Authorization, Content-Type

#### Production Mode
When `APP_ENV=production`:
- Only specified production domains allowed
- Must be configured via `CORS_ALLOWED_ORIGINS` environment variable
- No wildcards for methods or headers

## 4. Input Validation & Sanitization ✅

### Files: 
- `apps/api/app/schemas/quotes.py`
- `apps/api/app/schemas/orders.py`

### Validations Implemented

#### Quote Creation
- Asset codes: uppercase letters and numbers only (A-Z, 0-9)
- Amount validation:
  - Must be positive (> 0)
  - Maximum limit: 1 billion
- Automatic uppercasing of asset codes

#### Order Creation
- UUID format validation for quote_id
- Required field validation

## 5. Rate Limiting ✅

### File: `apps/api/app/main.py`, endpoint files

Using SlowAPI for rate limiting:
- **Quotes**: 30 requests per minute per IP
- **Orders**: 10 requests per minute per IP

### Response on Limit Exceeded
```json
{
  "detail": "Rate limit exceeded"
}
```
HTTP Status: 429 Too Many Requests

### Headers
Rate limit information exposed via headers:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`

## 6. Audit Logging ✅

### File: `docs/operations/audit-logging.md`

All financial operations are logged:
- Quote creation
- Order creation/execution/cancellation
- User ID association for all operations
- Timestamps in UTC
- Operation details

### Log Format
```
INFO: Quote created: id=<uuid>, user_id=<uuid>, sell=<amount> <asset>, buy_asset=<asset>
INFO: Order creation requested: quote_id=<uuid>, user_id=<uuid>, timestamp=<ISO8601>
```

## 7. Swagger UI Protection ✅

### File: `apps/api/app/main.py`

Swagger documentation is automatically disabled in production:
```python
docs_url="/docs" if settings.app_env != "production" else None
```

In production (`APP_ENV=production`):
- `/docs` endpoint returns 404
- API schema not publicly exposed

## Quick Start (Development)

1. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

2. Generate secure values:
   ```bash
   # In .env file, replace:
   # POSTGRES_PASSWORD=your_secure_password_here_change_in_production
   # JWT_SECRET=your-super-secret-jwt-key-change-this-in-production-min-32-chars
   ```

3. Start services:
   ```bash
   docker-compose up -d
   ```

4. Test authentication (example):
   ```python
   from app.core.security import create_access_token
   from uuid import uuid4
   
   # Generate a test token
   token = create_access_token(user_id=uuid4())
   print(f"Use this token: {token}")
   ```

## Production Checklist

- [ ] Change `APP_ENV` to `production`
- [ ] Generate strong `POSTGRES_PASSWORD` (min 32 chars)
- [ ] Generate strong `JWT_SECRET` (min 32 chars)
- [ ] Set `CORS_ALLOWED_ORIGINS` to your production domains
- [ ] Never commit `.env` file to version control
- [ ] Use secrets manager for sensitive values in production
- [ ] Enable HTTPS/TLS for all communications
- [ ] Configure log shipping to secure storage
- [ ] Set up monitoring for failed authentication attempts
- [ ] Review and rotate API keys regularly

## Additional Security Recommendations

1. **Database**: Use SSL/TLS connections in production
2. **Redis**: Enable authentication and restrict network access
3. **Monitoring**: Set up alerts for unusual patterns
4. **Backups**: Encrypt database backups
5. **Updates**: Keep all dependencies updated
6. **Penetration Testing**: Regular security audits
