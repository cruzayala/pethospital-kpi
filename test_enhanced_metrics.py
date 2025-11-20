# coding: utf-8
"""
Test script for enhanced metrics endpoint (v2.1)

Tests the new /kpi/submit/enhanced endpoint with intelligent metrics
"""
import sys
import requests
from datetime import date

BASE_URL = "http://localhost:8000"
CENTER_CODE = "HVC"
API_KEY = "test-api-key-local-HVC-2025"

print("=" * 70)
print("TEST ENHANCED METRICS ENDPOINT - v2.1")
print("=" * 70)

# Test payload with all enhanced metrics
enhanced_payload = {
    "center_code": CENTER_CODE,
    "date": date.today().isoformat(),

    # Original metrics (backward compatible)
    "total_orders": 50,
    "total_results": 45,
    "total_pets": 30,
    "total_owners": 25,

    "tests": [
        {"code": "GLU", "name": "Glucosa", "count": 15},
        {"code": "BUN", "name": "Nitrogeno Ureico", "count": 12},
        {"code": "ALT", "name": "Alanina Aminotransferasa", "count": 10}
    ],

    "species": [
        {"species": "Canino", "count": 20},
        {"species": "Felino", "count": 10}
    ],

    "breeds": [
        {"breed": "Labrador", "species": "Canino", "count": 8},
        {"breed": "Chihuahua", "species": "Canino", "count": 6},
        {"breed": "Persa", "species": "Felino", "count": 5}
    ],

    # Enhanced metrics v2.1
    "performance": {
        "avg_order_processing_time": 120,  # 2 hours average
        "peak_hour": 14,                   # 2 PM
        "peak_hour_orders": 12,
        "completion_rate": 90,             # 90% completion rate
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
            "total_revenue": 15000,  # $150.00 in cents
            "avg_transaction": 300   # $3.00 in cents
        },
        {
            "module_name": "consultas",
            "operations_count": 30,
            "active_users": 2,
            "total_revenue": 9000,
            "avg_transaction": 300
        },
        {
            "module_name": "farmacia",
            "operations_count": 20,
            "active_users": 1,
            "total_revenue": 5000,
            "avg_transaction": 250
        }
    ],

    "system_usage": {
        "total_active_users": 5,
        "peak_concurrent_users": 3,
        "avg_session_duration": 180,  # 3 hours average session
        "web_access_count": 100,
        "mobile_access_count": 20,
        "desktop_access_count": 50,
        "total_workstations": 4
    },

    "payment_methods": [
        {"payment_method": "efectivo", "transaction_count": 20, "total_amount": 8000},
        {"payment_method": "tarjeta", "transaction_count": 15, "total_amount": 10000},
        {"payment_method": "transferencia", "transaction_count": 10, "total_amount": 6000},
        {"payment_method": "seguro", "transaction_count": 5, "total_amount": 5000}
    ]
}

try:
    print("\n[Test 1] Submitting enhanced metrics...")
    print(f"Endpoint: POST {BASE_URL}/kpi/submit/enhanced")
    print(f"Center: {CENTER_CODE}")
    print(f"Date: {date.today().isoformat()}")

    # Submit with API key in header (recommended)
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"{BASE_URL}/kpi/submit/enhanced",
        json=enhanced_payload,
        headers=headers,
        timeout=10
    )

    if response.status_code == 201:
        result = response.json()
        print(f"\n[OK] Enhanced metrics submitted successfully!")
        print(f"\nResponse:")
        print(f"  Center: {result['center']}")
        print(f"  Date: {result['date']}")
        print(f"  Message: {result['message']}")
        print(f"\n  Saved:")
        print(f"    - Daily metrics: {result['saved']['daily_metrics']}")
        print(f"    - Tests: {result['saved']['tests']}")
        print(f"    - Species: {result['saved']['species']}")
        print(f"    - Breeds: {result['saved']['breeds']}")
        print(f"    - Performance: {result['saved']['performance']}")
        print(f"    - Modules: {result['saved']['modules']}")
        print(f"    - System usage: {result['saved']['system_usage']}")
        print(f"    - Payment methods: {result['saved']['payment_methods']}")
    else:
        print(f"\n[ERROR] Request failed with status: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("[SUCCESS] ALL TESTS PASSED!")
    print("=" * 70)

    print("\nEnhanced metrics features:")
    print("  - Performance tracking: Processing times, peak hours, completion rates")
    print("  - Module analytics: Usage by laboratorio, consultas, farmacia, etc.")
    print("  - System usage: Active users, sessions, access types (web/mobile/desktop)")
    print("  - Payment methods: Cash, card, transfer, insurance distribution")

    print("\nYou can now:")
    print(f"  - View dashboard: {BASE_URL}/")
    print(f"  - API documentation: {BASE_URL}/docs")
    print(f"  - Get center metrics: {BASE_URL}/kpi/centers/{CENTER_CODE}/metrics")

except requests.exceptions.ConnectionError:
    print("\n[ERROR] Cannot connect to server")
    print("Make sure the server is running on http://localhost:8000")
    sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
