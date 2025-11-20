# Enhanced Metrics v2.1 - Intelligent Analytics

## Overview

Enhanced Metrics v2.1 adds intelligent analytics capabilities to the PetHospital KPI service, tracking performance, module usage, system metrics, and payment methods while maintaining privacy-first design (no PII).

## New Features

### 1. Performance Metrics
Track operational efficiency and workload distribution:

- **Processing Times**: Average time from order to result completion
- **Peak Hours**: Identify busiest hours and optimize staffing
- **Completion Rates**: Monitor order fulfillment efficiency
- **Workload Distribution**: Orders by time of day (morning/afternoon/evening/night)

**Privacy Note**: All metrics are aggregated. No individual order data is stored.

### 2. Module Usage Metrics
Analyze which system modules are being used:

- **Module Activity**: Operations count per module (laboratorio, consultas, farmacia, etc.)
- **User Engagement**: Number of active users per module
- **Revenue Tracking**: Optional aggregated revenue per module
- **Transaction Analytics**: Average transaction values

**Privacy Note**: User counts are aggregated (no names, IDs, or identifiable information).

### 3. System Usage Metrics
Monitor system access and utilization:

- **Active Users**: Total users active each day
- **Concurrent Users**: Peak simultaneous users
- **Session Duration**: Average session length
- **Access Distribution**: Web vs mobile vs desktop usage
- **Workstation Count**: Number of active workstations

**Privacy Note**: No user names, IDs, or session identifiers are stored.

### 4. Payment Method Metrics
Track payment method distribution:

- **Payment Types**: efectivo, tarjeta, transferencia, seguro, etc.
- **Transaction Counts**: Number of transactions per payment method
- **Revenue Distribution**: Amount collected by payment method

**Privacy Note**: All amounts are aggregated. No individual transaction details are stored.

## API Endpoints

### POST /kpi/submit/enhanced

Submit enhanced daily metrics from a center.

**Authentication**: X-API-Key header (recommended) or api_key in body (deprecated)

**Request Example**:
```bash
curl -X POST "http://localhost:8000/kpi/submit/enhanced" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "center_code": "HVC",
    "date": "2025-11-19",
    "total_orders": 50,
    "total_results": 45,
    "total_pets": 30,
    "total_owners": 25,
    "tests": [
      {"code": "GLU", "name": "Glucosa", "count": 15}
    ],
    "species": [
      {"species": "Canino", "count": 20}
    ],
    "breeds": [
      {"breed": "Labrador", "species": "Canino", "count": 8}
    ],
    "performance": {
      "avg_order_processing_time": 120,
      "peak_hour": 14,
      "peak_hour_orders": 12,
      "completion_rate": 90,
      "same_day_completion": 40,
      "morning_orders": 15,
      "afternoon_orders": 25,
      "evening_orders": 8,
      "night_orders": 2
    },
    "modules": [
      {
        "module_name": "laboratorio",
        "operations_count": 50,
        "active_users": 3,
        "total_revenue": 15000,
        "avg_transaction": 300
      }
    ],
    "system_usage": {
      "total_active_users": 5,
      "peak_concurrent_users": 3,
      "avg_session_duration": 180,
      "web_access_count": 100,
      "mobile_access_count": 20,
      "desktop_access_count": 50,
      "total_workstations": 4
    },
    "payment_methods": [
      {"payment_method": "efectivo", "transaction_count": 20, "total_amount": 8000}
    ]
  }'
```

**Response Example**:
```json
{
  "message": "Enhanced metrics submitted successfully",
  "center": "Hospital Veterinario Central",
  "date": "2025-11-19",
  "saved": {
    "daily_metrics": true,
    "tests": 1,
    "species": 1,
    "breeds": 1,
    "performance": true,
    "modules": 1,
    "system_usage": true,
    "payment_methods": 1
  }
}
```

## Database Schema

### performance_metrics Table
```sql
CREATE TABLE performance_metrics (
    id SERIAL PRIMARY KEY,
    center_id INTEGER REFERENCES centers(id),
    date DATE NOT NULL,
    avg_order_processing_time INTEGER,  -- in minutes
    peak_hour INTEGER,                   -- 0-23
    peak_hour_orders INTEGER,
    completion_rate INTEGER,             -- 0-100
    same_day_completion INTEGER,
    morning_orders INTEGER DEFAULT 0,    -- 6am-12pm
    afternoon_orders INTEGER DEFAULT 0,  -- 12pm-6pm
    evening_orders INTEGER DEFAULT 0,    -- 6pm-12am
    night_orders INTEGER DEFAULT 0,      -- 12am-6am
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### module_metrics Table
```sql
CREATE TABLE module_metrics (
    id SERIAL PRIMARY KEY,
    center_id INTEGER REFERENCES centers(id),
    date DATE NOT NULL,
    module_name VARCHAR(100) NOT NULL,   -- laboratorio, consultas, farmacia
    operations_count INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    total_revenue INTEGER,               -- in cents
    avg_transaction INTEGER,             -- in cents
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### system_usage_metrics Table
```sql
CREATE TABLE system_usage_metrics (
    id SERIAL PRIMARY KEY,
    center_id INTEGER REFERENCES centers(id),
    date DATE NOT NULL,
    total_active_users INTEGER DEFAULT 0,
    peak_concurrent_users INTEGER DEFAULT 0,
    avg_session_duration INTEGER,        -- in minutes
    web_access_count INTEGER DEFAULT 0,
    mobile_access_count INTEGER DEFAULT 0,
    desktop_access_count INTEGER DEFAULT 0,
    total_workstations INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### payment_method_metrics Table
```sql
CREATE TABLE payment_method_metrics (
    id SERIAL PRIMARY KEY,
    center_id INTEGER REFERENCES centers(id),
    date DATE NOT NULL,
    payment_method VARCHAR(50) NOT NULL,  -- efectivo, tarjeta, transferencia, seguro
    transaction_count INTEGER DEFAULT 0,
    total_amount INTEGER,                 -- in cents
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Implementation Guide

### Step 1: Initialize Database Tables
Run the initialization script to create new tables:

```bash
python init_enhanced_metrics.py
```

Or apply the SQL migration directly:

```bash
psql -U postgres -d pethospital_kpi -f migration_v2_1_enhanced_metrics.sql
```

### Step 2: Update Your Integration
Modify your data collection code to gather enhanced metrics:

```python
from datetime import date

# Collect enhanced metrics from your system
enhanced_data = {
    "center_code": "YOUR_CENTER_CODE",
    "date": date.today().isoformat(),

    # Original metrics (required)
    "total_orders": get_order_count(),
    "total_results": get_result_count(),
    "total_pets": get_pet_count(),
    "total_owners": get_owner_count(),

    # Optional: Enhanced metrics
    "performance": {
        "avg_order_processing_time": calculate_avg_processing_time(),
        "peak_hour": get_peak_hour(),
        "completion_rate": calculate_completion_rate()
    },

    "modules": [
        {
            "module_name": "laboratorio",
            "operations_count": get_lab_operations(),
            "active_users": count_lab_users()
        }
    ]
}

# Submit to KPI service
import requests
response = requests.post(
    "http://your-kpi-service.com/kpi/submit/enhanced",
    json=enhanced_data,
    headers={"X-API-Key": "your-api-key"}
)
```

### Step 3: Test the Integration
Use the provided test script:

```bash
python test_enhanced_metrics.py
```

## Backward Compatibility

Enhanced Metrics v2.1 is **fully backward compatible**:

- **Original endpoint** `/kpi/submit` continues to work unchanged
- **Enhanced endpoint** `/kpi/submit/enhanced` accepts all original fields plus new metrics
- All enhanced metrics are **optional** - submit only what you have
- Existing integrations require **no changes**

## Privacy & Security

### What We Track (Aggregated Only)
- Performance metrics (timing, counts, percentages)
- Module usage statistics (counts, revenue totals)
- System access counts (web/mobile/desktop)
- Payment method distribution (counts, totals)

### What We DO NOT Track
- Individual patient/pet names or IDs
- Individual owner names or contact information
- Specific transaction details
- User names or personal identifiers
- Session identifiers or tokens
- IP addresses or device identifiers

### Revenue Storage
Revenue is stored in **cents** (integer) to avoid decimal precision issues:
- Store: 15000 = $150.00
- Store: 300 = $3.00

## Analytics Use Cases

### 1. Optimize Staffing
Use peak hour analysis to schedule staff during busiest times:
- Identify peak hours across centers
- Compare weekday vs weekend patterns
- Adjust shifts based on workload distribution

### 2. Module Adoption
Track which features are being used:
- Identify underutilized modules
- Compare adoption across centers
- Calculate ROI per module

### 3. Performance Monitoring
Monitor operational efficiency:
- Track processing time trends
- Set completion rate targets
- Identify bottlenecks

### 4. Financial Analytics
Understand revenue distribution:
- Track payment method preferences
- Identify cash vs digital payment trends
- Optimize payment processing

## Dashboard Visualizations

The enhanced dashboard will display:

1. **Performance Charts**
   - Average processing time trend
   - Peak hour heatmap
   - Completion rate gauge
   - Workload distribution by time of day

2. **Module Usage**
   - Operations by module (bar chart)
   - Active users per module
   - Revenue by module (optional)

3. **System Access**
   - Web vs mobile vs desktop distribution (pie chart)
   - Concurrent users trend
   - Session duration average

4. **Payment Methods**
   - Payment method distribution (pie chart)
   - Transaction counts by method
   - Revenue by payment type

## Troubleshooting

### Issue: "Invalid center code or API key"
**Solution**: Ensure your center is registered and API key is correct.

```bash
# Register a test center
python register_hvc.py
```

### Issue: Enhanced metrics not appearing in dashboard
**Solution**: Make sure database tables are created:

```bash
python init_enhanced_metrics.py
```

### Issue: Revenue values incorrect
**Solution**: Remember to convert to cents (multiply by 100):

```python
# Wrong
"total_revenue": 150.00  # Don't use decimals

# Correct
"total_revenue": 15000   # $150.00 in cents
```

## Roadmap

### Future Enhancements
- **AI/ML Predictions**: Forecast order volumes based on historical patterns
- **Anomaly Detection**: Alert on unusual patterns (spikes, drops)
- **Comparative Analytics**: Benchmark centers against each other
- **Trend Analysis**: Identify growth opportunities
- **Custom Dashboards**: Per-center customizable views

## Support

For questions or issues:
- API Documentation: http://your-kpi-service.com/docs
- GitHub Issues: https://github.com/your-org/pethospital-kpi/issues

## Version History

### v2.1 (2025-11-19)
- Added performance metrics (processing times, peak hours, completion rates)
- Added module usage metrics (operations, users, revenue per module)
- Added system usage metrics (users, sessions, access types)
- Added payment method metrics (distribution, counts, amounts)
- New endpoint: POST /kpi/submit/enhanced
- Full backward compatibility maintained

### v2.0 (2025-11-17)
- Production-ready version with security hardening
- Authentication via X-API-Key headers
- Rate limiting
- Structured logging
- Global exception handling

### v1.0 (2025-11-13)
- MVP/Beta release
- Basic metrics collection
