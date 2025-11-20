# Railway Deployment Guide - PetHospital KPI Service

Complete guide for deploying the PetHospital KPI Service to Railway.

## Table of Contents
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Deployment Steps](#deployment-steps)
- [Post-Deployment Verification](#post-deployment-verification)
- [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

Before deploying to Railway, ensure:

- [ ] Python 3.12 compatibility verified (requirements.txt uses Pydantic v2)
- [ ] All security credentials changed from defaults
- [ ] Database migrations are up to date
- [ ] `.env.example` is complete and accurate
- [ ] GitHub repository is up to date
- [ ] Local testing completed successfully

---

## Environment Variables

### Required Variables (Railway)

Railway automatically provides these variables:

| Variable | Description | Auto-Provided |
|----------|-------------|---------------|
| `DATABASE_URL` | PostgreSQL connection string | Yes (when PostgreSQL addon added) |
| `PORT` | Application port | Yes |

### Required Variables (Manual Configuration)

Configure these in Railway's environment variables:

#### Critical Security Variables

```bash
# JWT Authentication - CRITICAL: Change in production
JWT_SECRET_KEY=<generate-long-random-string>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Center API Key - CRITICAL: Change in production
CENTER_API_KEY=<your-secure-api-key>

# Dashboard Authentication - CRITICAL: Change in production
DASHBOARD_USERNAME=<your-admin-username>
DASHBOARD_PASSWORD=<your-secure-password>
```

**How to generate secure keys:**
```bash
# Generate JWT_SECRET_KEY (Python)
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Generate CENTER_API_KEY
python -c "import secrets; print('codex-' + secrets.token_urlsafe(32))"
```

#### Application Configuration

```bash
# Application
APP_TITLE=PetHospital KPI Service
APP_VERSION=2.0.0
ENVIRONMENT=production
LOG_LEVEL=INFO
ENABLE_DOCS=false  # Disable in production for security

# CORS - Restrict to your domains
ALLOWED_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com

# Rate Limiting
RATE_LIMIT_SUBMIT=100/day
RATE_LIMIT_EVENTS=1000/day
RATE_LIMIT_DASHBOARD=60/minute
```

#### Optional - Monitoring

```bash
# Sentry (optional - error tracking)
SENTRY_DSN=<your-sentry-dsn>
```

#### Optional - Caching (Redis)

```bash
# Redis (optional - for production performance)
REDIS_URL=<railway-redis-url>
CACHE_ENABLED=true
CACHE_TTL_DEFAULT=300
```

---

## Database Setup

### Step 1: Add PostgreSQL to Railway

1. In your Railway project, click **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway will automatically set the `DATABASE_URL` environment variable
3. Wait for the database to be provisioned (usually 30-60 seconds)

### Step 2: Run Migrations

Railway does NOT automatically run database migrations. You have two options:

#### Option A: Manual Migration (Recommended for first deployment)

1. Connect to Railway PostgreSQL from your local machine:
   ```bash
   # Get connection details from Railway dashboard
   railway run psql
   ```

2. Run migrations manually:
   ```bash
   # Navigate to project directory
   cd pethospital-kpi

   # Run all migrations
   python run_migrations.py
   ```

#### Option B: Add Migration Command to railway.json

Modify `railway.json` to run migrations on deploy:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python run_migrations.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10,
    "healthcheckPath": "/api/config/health",
    "healthcheckTimeout": 100
  }
}
```

**Note:** This runs migrations on every deploy. For production, manual migrations are safer.

### Step 3: Create Admin User

After migrations, create your first admin user:

```bash
# Connect to Railway database
railway run python

# In Python shell:
from app.database import SessionLocal
from app.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

admin = User(
    username="admin",
    email="admin@yourcompany.com",
    hashed_password=pwd_context.hash("YourSecurePassword123!"),
    full_name="System Administrator",
    is_active=True,
    is_superuser=True
)
db.add(admin)
db.commit()
print(f"Admin user created: {admin.username}")
```

---

## Deployment Steps

### Step 1: Push to GitHub

```bash
# Ensure all changes are committed
git add .
git commit -m "Railway deployment configuration"
git push origin main
```

### Step 2: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository: `pethospital-kpi`
5. Railway will automatically detect the Python project

### Step 3: Add PostgreSQL Database

1. In your Railway project, click **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Wait for provisioning

### Step 4: Configure Environment Variables

1. Go to your service → **"Variables"** tab
2. Add all required environment variables (see [Environment Variables](#environment-variables))
3. Click **"Deploy"**

### Step 5: Verify Deployment

Railway will automatically:
- Detect Python 3.12 (from `runtime.txt`)
- Install dependencies (from `requirements.txt`)
- Run the start command (from `railway.json`)
- Perform health checks on `/api/config/health`

---

## Post-Deployment Verification

### 1. Check Service Status

Visit Railway dashboard → Your service → **"Deployments"** tab
- Status should show **"Active"**
- Health check should be **"Passing"**

### 2. Test Public Endpoints

```bash
# Get your Railway URL from dashboard
export RAILWAY_URL=https://your-app.railway.app

# Test health endpoint
curl $RAILWAY_URL/api/config/health
# Expected: {"status": "healthy", "database": "connected", ...}

# Test login page
curl $RAILWAY_URL/dashboard/login
# Expected: HTML content
```

### 3. Test Authentication

```bash
# Test login
curl -X POST $RAILWAY_URL/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=YourPassword"
# Expected: {"access_token": "...", "token_type": "bearer"}
```

### 4. Verify Protected Endpoints

```bash
# Get access token first
TOKEN=$(curl -X POST $RAILWAY_URL/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=YourPassword" | jq -r '.access_token')

# Test protected endpoint
curl $RAILWAY_URL/api/analytics/summary \
  -H "Authorization: Bearer $TOKEN"
# Expected: Analytics data
```

### 5. Check Logs

```bash
# Using Railway CLI
railway logs

# Or view in Railway dashboard → Deployments → View Logs
```

---

## Troubleshooting

### Issue: "Application failed to respond"

**Possible Causes:**
1. Wrong `$PORT` binding
2. Database connection failure
3. Missing environment variables

**Solutions:**
```bash
# Verify Procfile and railway.json use $PORT
# Check: uvicorn app.main:app --host 0.0.0.0 --port $PORT

# Verify DATABASE_URL is set
railway variables

# Check application logs
railway logs
```

### Issue: "TypeError: ForwardRef._evaluate()"

**Cause:** Pydantic v1 incompatible with Python 3.12

**Solution:**
```bash
# Ensure requirements.txt has:
pydantic==2.6.1  # NOT 1.10.x
fastapi==0.109.2  # Compatible with Pydantic v2
```

### Issue: "ImportError: email-validator not installed"

**Cause:** Missing email-validator package

**Solution:**
```bash
# Add to requirements.txt:
email-validator==2.1.0
```

### Issue: Database connection errors

**Symptoms:**
```
sqlalchemy.exc.OperationalError: connection to server failed
```

**Solutions:**
1. Verify PostgreSQL addon is added to Railway project
2. Check `DATABASE_URL` environment variable is set
3. Verify `postgres://` is converted to `postgresql://` (done in `app/database.py`)

**Check connection:**
```bash
# Connect via Railway CLI
railway run psql

# If successful, database is working
```

### Issue: Health check failing

**Symptoms:**
```
Health check timeout on /api/config/health
```

**Solutions:**
1. Verify endpoint exists and is accessible
   ```bash
   curl https://your-app.railway.app/api/config/health
   ```

2. Increase timeout in `railway.json`:
   ```json
   "healthcheckTimeout": 200
   ```

3. Check application logs for startup errors

### Issue: JWT authentication not working

**Symptoms:**
```
{"detail": "Could not validate credentials"}
```

**Solutions:**
1. Verify `JWT_SECRET_KEY` is set in Railway environment variables
2. Ensure it matches the key used to generate tokens
3. Check token hasn't expired (`JWT_ACCESS_TOKEN_EXPIRE_MINUTES`)

---

## Performance Optimization

### Connection Pool Settings

The `app/database.py` is already optimized for Railway with:

```python
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Verify connections before using
    pool_size=5,             # Connections in pool
    max_overflow=10,         # Extra connections allowed
    pool_recycle=3600,       # Recycle connections every hour
    echo=False               # Don't log SQL queries
)
```

### Redis Caching (Optional)

For better performance, add Redis:

1. In Railway project: **New** → **Database** → **Add Redis**
2. Set environment variables:
   ```bash
   CACHE_ENABLED=true
   CACHE_TTL_DEFAULT=300
   ```

---

## Security Checklist

Before going to production:

- [ ] `JWT_SECRET_KEY` changed from default
- [ ] `CENTER_API_KEY` changed from default
- [ ] `DASHBOARD_USERNAME` changed from "admin"
- [ ] `DASHBOARD_PASSWORD` changed from default
- [ ] `ALLOWED_ORIGINS` restricted (not "*")
- [ ] `ENABLE_DOCS` set to false
- [ ] `ENVIRONMENT` set to "production"
- [ ] Admin user password is strong (8+ chars, mixed case, numbers, symbols)
- [ ] SSL/HTTPS enabled (Railway does this automatically)
- [ ] Database backups configured (Railway PostgreSQL auto-backups)

---

## Monitoring & Maintenance

### View Logs

```bash
# Real-time logs
railway logs --follow

# Last 100 lines
railway logs -n 100
```

### Database Backups

Railway PostgreSQL includes automatic daily backups. To manually backup:

```bash
# Export database
railway run pg_dump > backup.sql

# Restore from backup
railway run psql < backup.sql
```

### Scaling

Railway automatically handles scaling based on your plan. For manual scaling:

1. Go to project → **Settings** → **Resources**
2. Adjust CPU/Memory limits
3. Consider upgrading to Railway Pro for better performance

---

## Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Pydantic v2 Migration](https://docs.pydantic.dev/latest/migration/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)

---

## Support

For issues specific to this application:
- Check logs: `railway logs`
- Review this documentation
- Verify all environment variables are set correctly

For Railway platform issues:
- [Railway Discord](https://discord.gg/railway)
- [Railway Support](https://railway.app/help)
