# Changelog - PetHospital KPI Service

All notable changes to this project will be documented in this file.

## [2.0.0] - 2025-11-19 - Production Ready Release

### 🔒 Security Enhancements

#### CORS Configuration
- **CHANGED**: CORS origins now configurable via `ALLOWED_ORIGINS` environment variable
- **REMOVED**: Default wildcard (`*`) CORS policy
- **ADDED**: Validation to prevent wildcard CORS in production
- **MIGRATION**: Set `ALLOWED_ORIGINS` in your `.env` file with comma-separated domains
  ```
  ALLOWED_ORIGINS=https://codex.example.com,https://admin.example.com
  ```

#### API Key Authentication
- **CHANGED**: API keys now accepted via `X-API-Key` header (recommended)
- **DEPRECATED**: API keys in request body (still supported for backward compatibility)
- **ADDED**: Deprecation warning logged when using body-based API keys
- **MIGRATION**: Update your API clients to send API key in header:
  ```bash
  curl -H "X-API-Key: your-key-here" https://kpi-service.com/kpi/submit
  ```

#### Dashboard Authentication
- **ADDED**: HTTP Basic Authentication for dashboard access
- **NEW ENV VARS**: `DASHBOARD_USERNAME` and `DASHBOARD_PASSWORD`
- **MIGRATION**: Set credentials in `.env`:
  ```
  DASHBOARD_USERNAME=admin
  DASHBOARD_PASSWORD=your-secure-password-here
  ```

#### Rate Limiting
- **ADDED**: Rate limiting on all endpoints
- **NEW ENV VARS**:
  - `RATE_LIMIT_SUBMIT` (default: 100/day)
  - `RATE_LIMIT_EVENTS` (default: 1000/day)
  - `RATE_LIMIT_DASHBOARD` (default: 60/minute)
- **RESPONSE**: 429 Too Many Requests when limit exceeded

---

### 📊 Monitoring & Logging

#### Structured Logging
- **ADDED**: Loguru-based structured logging system
- **NEW ENV VAR**: `LOG_LEVEL` (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **FEATURES**:
  - JSON format logs in production
  - Human-readable logs in development
  - Automatic log rotation (daily)
  - Separate error log file
  - 30-day log retention

#### Sentry Integration
- **ADDED**: Error tracking and performance monitoring via Sentry
- **NEW ENV VAR**: `SENTRY_DSN` (optional)
- **FEATURES**:
  - Automatic error capture
  - Performance tracing
  - FastAPI and SQLAlchemy integrations
  - No PII sent to Sentry

#### Health Checks
- **IMPROVED**: `/health` endpoint now returns version and environment
- **NEW**: `/health/ready` endpoint for readiness probes (checks database)
- **USE CASE**: Kubernetes liveness and readiness probes

---

### 🏗️ Architecture Improvements

#### Configuration Management
- **ADDED**: Centralized configuration system (`app/config.py`)
- **FEATURES**:
  - Type-safe settings
  - Environment-based configuration
  - Startup validation
  - Production safety checks

#### Exception Handling
- **ADDED**: Global exception handlers for consistent error responses
- **STANDARD**: RFC 7807 Problem Details format
- **HANDLES**:
  - Validation errors (422)
  - Database integrity errors (409)
  - Database connection errors (503)
  - Generic SQLAlchemy errors (500)
  - Unexpected exceptions (500)

#### Middleware
- **ADDED**: Request logging middleware (logs all HTTP requests)
- **ADDED**: GZip compression middleware (responses > 1KB)
- **IMPROVED**: CORS middleware with restrictive defaults

---

### 🚀 Performance Optimizations

- **ADDED**: Response compression (GZip) for large payloads
- **IMPROVED**: Database connection handling
- **IMPROVED**: Error handling performance

---

### 📝 API Changes

#### New Endpoints
- `GET /health/ready` - Readiness check with database verification

#### Modified Endpoints
- `POST /kpi/submit` - Now accepts X-API-Key header, added rate limiting
- `POST /kpi/events` - Now accepts X-API-Key header, added rate limiting
- `GET /` (dashboard) - Now requires HTTP Basic Auth, added rate limiting
- `GET /health` - Enhanced response with version and environment info

#### Deprecated
- API keys in request body (use X-API-Key header instead)

---

### 📚 Documentation

#### New Files
- `CHANGELOG.md` - This file
- `MIGRATION-GUIDE.md` - Step-by-step migration guide
- `SECURITY.md` - Security best practices

#### Updated Files
- `.env.example` - All new environment variables documented
- `README.md` - Updated with v2.0 features
- `LOCAL_TESTING.md` - Updated with new authentication steps
- `RAILWAY_SETUP.md` - Updated with new environment variables

---

### 🔧 Dependencies

#### Added
- `slowapi==0.1.9` - Rate limiting
- `passlib[bcrypt]==1.7.4` - Password hashing for dashboard auth
- `loguru==0.7.2` - Structured logging
- `sentry-sdk[fastapi]==1.39.2` - Error monitoring
- `alembic==1.13.1` - Database migrations (for future use)

#### Updated
- No version changes for existing dependencies

---

### 💥 Breaking Changes

1. **Dashboard Access**: Dashboard now requires authentication
   - **Action Required**: Set `DASHBOARD_USERNAME` and `DASHBOARD_PASSWORD`

2. **CORS Policy**: Default CORS is no longer wildcard
   - **Action Required**: Set `ALLOWED_ORIGINS` for production
   - **Workaround**: Use `ALLOWED_ORIGINS=*` for testing (not recommended)

3. **Rate Limiting**: All endpoints now rate-limited
   - **Impact**: High-frequency requests may be throttled
   - **Action**: Adjust rate limits via environment variables if needed

---

### 🐛 Bug Fixes

- Fixed potential timing attack in dashboard authentication (using constant-time comparison)
- Improved database connection error handling
- Better handling of malformed requests

---

### 🔐 Security Fixes

- **CVE-NONE**: No known vulnerabilities, but security posture significantly improved
- Reduced attack surface with restrictive CORS
- Added authentication to previously public dashboard
- Implemented rate limiting to prevent abuse

---

## [1.0.0] - 2025-01-14 - Initial Release

### Features
- Basic KPI collection from multiple centers
- Dashboard with Chart.js visualizations
- PostgreSQL database
- Railway.app deployment support
- Batch and real-time event processing
- Auto-registration of centers

---

## Migration Path

### From 1.0.0 to 2.0.0

See [MIGRATION-GUIDE.md](MIGRATION-GUIDE.md) for detailed step-by-step instructions.

**Quick Summary**:
1. Update dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and configure new variables
3. Update API clients to use `X-API-Key` header
4. Set dashboard credentials
5. Configure CORS origins for production
6. Optional: Configure Sentry for error tracking

---

## Versioning

This project uses [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

---

## Support

- **Issues**: https://github.com/your-org/pethospital-kpi/issues
- **Discussions**: https://github.com/your-org/pethospital-kpi/discussions
- **Email**: support@your-domain.com
