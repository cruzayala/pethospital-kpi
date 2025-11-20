# Security Policy - PetHospital KPI Service

## 🔒 Security Overview

PetHospital KPI Service v2.0 has been designed with security as a top priority. This document outlines our security measures, best practices, and how to report vulnerabilities.

---

## 🛡️ Security Features

### 1. Authentication & Authorization

#### API Key Authentication
- **Method**: API keys via `X-API-Key` header
- **Storage**: Keys stored in database (not encrypted by default)
- **Validation**: Constant-time comparison to prevent timing attacks
- **Recommendation**: Use strong, randomly-generated API keys (min. 32 characters)

#### Dashboard Authentication
- **Method**: HTTP Basic Authentication
- **Credentials**: Configurable via environment variables
- **Protection**: Constant-time password comparison
- **Recommendation**: Use strong passwords (min. 16 characters, mixed case, numbers, symbols)

### 2. Rate Limiting

Prevents abuse and DoS attacks:

| Endpoint | Default Limit | Configurable |
|----------|---------------|--------------|
| `/kpi/submit` | 100/day per IP | `RATE_LIMIT_SUBMIT` |
| `/kpi/events` | 1000/day per IP | `RATE_LIMIT_EVENTS` |
| `/` (dashboard) | 60/minute per IP | `RATE_LIMIT_DASHBOARD` |
| `/health` | 60/minute per IP | Hardcoded |

**Response**: `429 Too Many Requests` when limit exceeded

### 3. CORS (Cross-Origin Resource Sharing)

- **Default**: Restrictive (no wildcard `*`)
- **Configuration**: `ALLOWED_ORIGINS` environment variable
- **Recommendation**: Only allow trusted domains in production

### 4. Input Validation

- **Framework**: Pydantic for request validation
- **Protection**: SQL injection, XSS, malformed data
- **Response**: `422 Unprocessable Entity` for invalid input

### 5. Error Handling

- **Production**: Generic error messages (no stack traces)
- **Development**: Detailed error information for debugging
- **Logging**: All errors logged with context

### 6. Data Privacy

#### What We Collect
- Aggregated counts (orders, results, pets, owners)
- Test codes and frequencies
- Species and breed distributions
- Center metadata (name, location)

#### What We DON'T Collect
- ❌ Owner names, addresses, phone numbers
- ❌ Pet names or individual records
- ❌ Medical test results or diagnoses
- ❌ Any Personally Identifiable Information (PII)
- ❌ Payment information

**GDPR/Privacy Compliance**: By design, this service doesn't handle personal data.

---

## 🔐 Security Best Practices

### For Production Deployment

#### 1. Environment Variables

**Required Security Settings**:
```bash
# Set strong dashboard credentials
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=<strong-password-here>

# Restrict CORS to your domains
ALLOWED_ORIGINS=https://your-codex-domain.com,https://admin-domain.com

# Set environment to production
ENVIRONMENT=production

# Disable API docs in production (optional)
ENABLE_DOCS=false
```

**API Key Management**:
```bash
# Use strong, unique API keys per center
# Example generation (Python):
import secrets
secrets.token_urlsafe(32)  # Generates 43-char key
```

#### 2. HTTPS/TLS

**Always use HTTPS in production**:
- Railway provides HTTPS automatically
- For custom domains, ensure SSL/TLS certificate is valid
- Never send API keys over HTTP

#### 3. Database Security

**PostgreSQL Security**:
```bash
# Use strong database password
DATABASE_URL=postgresql://user:STRONG_PASSWORD@host:5432/db

# Railway handles this automatically
# For self-hosted: restrict access by IP
```

**Backup Strategy**:
- Regular automated backups (daily recommended)
- Test restore procedures monthly
- Store backups encrypted

#### 4. Secrets Management

**Never commit secrets to git**:
```bash
# .gitignore should include:
.env
.env.local
.env.production
*.pem
*.key
```

**For Railway**:
- Use Railway's environment variables dashboard
- Never hardcode secrets in code

#### 5. Monitoring & Alerting

**Enable Sentry**:
```bash
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
```

**Monitor for**:
- Unusual rate of 401 errors (possible brute force)
- 429 errors (DoS attempts)
- 500 errors (application issues)
- Sudden drop in requests (service down)

#### 6. Rate Limit Tuning

**Adjust based on usage**:
```bash
# For high-traffic centers
RATE_LIMIT_SUBMIT=500/day
RATE_LIMIT_EVENTS=5000/day

# For internal-only dashboards
RATE_LIMIT_DASHBOARD=30/minute
```

#### 7. Regular Updates

**Keep dependencies up to date**:
```bash
# Check for security updates
pip list --outdated

# Update dependencies
pip install --upgrade <package>
```

**Subscribe to security advisories**:
- FastAPI security announcements
- SQLAlchemy security bulletins
- Pydantic security updates

---

## 🚨 Known Security Considerations

### 1. API Keys in Database

**Issue**: API keys stored in plaintext in database

**Risk**: If database is compromised, keys are exposed

**Mitigation Options**:
- Use bcrypt hashing (requires migration)
- Rotate keys regularly
- Use database encryption at rest (Railway provides this)

**Workaround**: Master key approach reduces exposure (all centers share key)

### 2. No Key Rotation

**Issue**: No automatic key expiration/rotation

**Risk**: Compromised keys remain valid indefinitely

**Mitigation**:
- Manual key rotation via database update
- Future: Implement key expiration in v3.0

### 3. Basic Auth for Dashboard

**Issue**: Basic Auth credentials sent with every request

**Risk**: If HTTPS is not used, credentials exposed

**Mitigation**:
- **Always use HTTPS**
- Use IP whitelisting for additional protection
- Future: Consider JWT-based auth in v3.0

### 4. Rate Limiting by IP

**Issue**: Rate limits can be bypassed with multiple IPs

**Risk**: Distributed DoS still possible

**Mitigation**:
- Use CDN/WAF for additional protection
- Monitor for patterns of abuse
- Implement account-level rate limiting (future)

---

## 🔍 Security Auditing

### Log Analysis

**Check authentication failures**:
```bash
grep "Invalid" logs/kpi-service_*.log | wc -l
```

**Check rate limit hits**:
```bash
grep "429" logs/kpi-service_*.log
```

**Check error patterns**:
```bash
grep "ERROR" logs/errors_*.log | tail -20
```

### Regular Security Checks

**Monthly**:
- [ ] Review access logs for anomalies
- [ ] Check for dependency updates
- [ ] Verify backup restoration works
- [ ] Review Sentry error reports

**Quarterly**:
- [ ] Rotate dashboard passwords
- [ ] Review API key usage
- [ ] Audit database access logs
- [ ] Penetration testing (optional)

**Annually**:
- [ ] Full security audit
- [ ] Rotate all API keys
- [ ] Review and update security policies

---

## 🐛 Reporting Security Vulnerabilities

### Please DO NOT open public GitHub issues for security vulnerabilities

Instead, report privately:

**Email**: security@your-domain.com

**Include**:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

**Response Time**:
- Acknowledgment: Within 48 hours
- Initial assessment: Within 7 days
- Fix (if confirmed): Within 30 days

**Disclosure Policy**:
- We follow responsible disclosure
- Public disclosure after fix is released
- Credit given to reporter (if desired)

---

## 📊 Security Incident Response

### If You Suspect a Breach

1. **Immediately**:
   - Change dashboard password
   - Rotate all API keys
   - Check logs for suspicious activity

2. **Within 24 hours**:
   - Review database for unauthorized changes
   - Check Railway deployment logs
   - Contact security@your-domain.com

3. **Within 48 hours**:
   - Conduct full security audit
   - Document incident timeline
   - Implement additional safeguards

### Sample Incident Log

```
Date: 2025-11-19
Time: 14:30 UTC
Incident: Suspicious 401 errors from IP 1.2.3.4
Actions Taken:
  - Blocked IP at firewall level
  - Verified no unauthorized access
  - Rotated API key for affected center
Resolution: False alarm - legitimate client with wrong key
Lessons Learned: Improve documentation for API clients
```

---

## 🔗 Security Resources

### Internal Documentation
- [MIGRATION-GUIDE.md](MIGRATION-GUIDE.md) - Secure migration procedures
- [CHANGELOG.md](CHANGELOG.md) - Security updates per version
- [README.md](README.md) - Setup and configuration

### External Resources
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/core/connections.html#sql-injection)

### Security Tools
- [Bandit](https://github.com/PyCQA/bandit) - Python security linter
- [Safety](https://github.com/pyupio/safety) - Dependency vulnerability scanner
- [OWASP ZAP](https://www.zaproxy.org/) - Web app security testing

---

## ✅ Security Checklist

Use this checklist for production deployment:

### Configuration
- [ ] Strong `DASHBOARD_PASSWORD` set
- [ ] `ALLOWED_ORIGINS` restricted to specific domains
- [ ] `ENVIRONMENT=production` set
- [ ] `ENABLE_DOCS=false` (or at least not advertised)
- [ ] Strong database password
- [ ] API keys are 32+ characters

### Infrastructure
- [ ] HTTPS enabled (automatic on Railway)
- [ ] Database backups configured
- [ ] Sentry error tracking enabled
- [ ] Rate limits appropriate for usage
- [ ] Logs monitored regularly

### Access Control
- [ ] Dashboard requires authentication
- [ ] API keys unique per center
- [ ] No secrets committed to git
- [ ] `.env` file has restrictive permissions (600)

### Monitoring
- [ ] Sentry notifications configured
- [ ] Log retention policy defined
- [ ] Security incident response plan documented
- [ ] Regular security audits scheduled

---

## 📞 Security Contacts

**Security Team**: security@your-domain.com
**General Support**: support@your-domain.com
**Emergency**: +1-XXX-XXX-XXXX (24/7 for critical issues)

---

## 📜 License & Legal

This security policy is part of the PetHospital KPI Service project.

**Last Updated**: 2025-11-19
**Version**: 2.0.0
