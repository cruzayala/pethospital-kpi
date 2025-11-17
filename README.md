# PetHospital KPI Service

Centralized KPI tracking service for multiple Codex Veterinaria installations.

## Features

- Collect aggregated metrics from multiple veterinary centers
- Beautiful dashboard with charts and statistics
- REST API for metric submission and retrieval
- No sensitive data stored (only metrics)
- Free deployment on Railway

## Architecture

```
Local Installations (Codex Veterinaria)
    |
    | POST /kpi/submit (daily)
    |
    v
Railway (FastAPI + PostgreSQL)
    |
    v
Dashboard (/) - View metrics
```

## What Data is Collected?

**Metrics only - NO sensitive data:**
- Daily order counts
- Test counts by type
- Species distribution
- Breed counts
- Pet counts (anonymous)

**NOT collected:**
- Owner names
- Pet names
- Addresses, phones
- Individual test results
- Any personal information

## Deploy to Railway

### Step 1: Create Railway Account

1. Go to https://railway.app
2. Sign up with GitHub
3. Free plan: $5 credit/month (more than enough)

### Step 2: Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Connect to this repository
4. Railway will auto-detect FastAPI

### Step 3: Add PostgreSQL

1. In your project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway auto-creates DATABASE_URL variable

### Step 4: Deploy

Railway automatically:
- Installs dependencies from requirements.txt
- Creates database tables
- Starts the service

Your service will be available at: `https://your-app.up.railway.app`

### Step 5: Register Centers

After deployment, you need to register each center in the database:

```sql
-- Connect to Railway PostgreSQL (use Railway's psql or GUI)
INSERT INTO centers (code, name, country, city, api_key, is_active)
VALUES
  ('HVC', 'Hospital Veterinario Central', 'Republica Dominicana', 'Santo Domingo', 'generate-random-key-here', 1);
```

**Generate API keys:**
```python
import secrets
api_key = secrets.token_urlsafe(32)
print(api_key)  # Use this for center's API key
```

## Local Development

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create local database
createdb pethospital_kpi

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Access

- Dashboard: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## API Endpoints

### Submit Metrics (from Codex installations)

```bash
POST /kpi/submit
Content-Type: application/json

{
  "center_code": "HVC",
  "api_key": "your-api-key-here",
  "date": "2025-11-13",
  "total_orders": 50,
  "total_results": 45,
  "total_pets": 30,
  "total_owners": 25,
  "tests": [
    {"code": "GLU", "name": "Glucosa", "count": 15},
    {"code": "BUN", "name": "Nitrogeno Ureico", "count": 12}
  ],
  "species": [
    {"species": "Canino", "count": 20},
    {"species": "Felino", "count": 10}
  ],
  "breeds": [
    {"breed": "Labrador", "species": "Canino", "count": 8}
  ]
}
```

### View Dashboard

```bash
GET /
```

### Get Center Metrics

```bash
GET /kpi/centers/{center_code}/metrics?days=30
```

### Get Summary Stats

```bash
GET /kpi/stats/summary?days=30
```

### List Centers

```bash
GET /kpi/centers
```

## Environment Variables

Railway automatically provides:
- `DATABASE_URL` - PostgreSQL connection
- `PORT` - Port to run on

No manual configuration needed!

## Security

- API key authentication for metric submission
- CORS enabled (restrict in production)
- No sensitive data stored
- Centers can be deactivated without data loss

## Monitoring

Check Railway dashboard for:
- CPU/Memory usage
- Database size
- Request logs
- Error rates

## Cost Estimation

Railway Free Plan ($5 credit/month):
- ~500 hours runtime (20+ days 24/7)
- 1GB PostgreSQL
- 100GB bandwidth

**Your usage (estimated):**
- 5 centers × 1 request/day = 150 requests/month
- Database: ~50MB after 1 year
- Bandwidth: <1GB/month

**Result: Completely FREE** for your use case!

## Support

For issues:
1. Check Railway logs
2. Check API docs at /docs
3. Verify API key is correct
4. Check database connection

## License

MIT License - Free to use and modify
