# coding: utf-8
"""
Test script for Analytics Modules

Tests all new analytics endpoints:
- Centers analytics
- Tests analytics
- Species & breeds analytics
"""
import sys
import requests

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("TEST ANALYTICS MODULES - Complete Suite")
print("=" * 70)

tests_passed = 0
tests_failed = 0

def test_endpoint(name, url):
    global tests_passed, tests_failed
    try:
        print(f"\n[Test] {name}")
        print(f"URL: GET {url}")
        r = requests.get(url, timeout=10)

        if r.status_code == 200:
            data = r.json()
            print(f"[OK] Status: {r.status_code}")
            print(f"[OK] Response keys: {list(data.keys())[:5]}...")
            tests_passed += 1
            return data
        else:
            print(f"[FAIL] Status: {r.status_code}")
            print(f"Response: {r.text[:200]}")
            tests_failed += 1
            return None
    except Exception as e:
        print(f"[ERROR] {e}")
        tests_failed += 1
        return None

try:
    # ========================================================================
    # CENTERS ANALYTICS
    # ========================================================================
    print("\n" + "=" * 70)
    print("CENTERS ANALYTICS")
    print("=" * 70)

    # Test 1: Center Summary
    test_endpoint(
        "Center Summary (HVC)",
        f"{BASE_URL}/analytics/centers/summary/HVC?days=30"
    )

    # Test 2: Centers Comparison
    test_endpoint(
        "Centers Comparison",
        f"{BASE_URL}/analytics/centers/comparison?days=30"
    )

    # Test 3: Center Trends
    test_endpoint(
        "Center Trends (HVC)",
        f"{BASE_URL}/analytics/centers/trends/HVC?days=30"
    )

    # ========================================================================
    # TESTS ANALYTICS
    # ========================================================================
    print("\n" + "=" * 70)
    print("TESTS ANALYTICS")
    print("=" * 70)

    # Test 4: Top Tests Global
    top_tests = test_endpoint(
        "Top Tests Global",
        f"{BASE_URL}/analytics/tests/top-global?days=30&limit=10"
    )

    # Test 5: Test Details (if we have test data)
    if top_tests and top_tests.get("tests") and len(top_tests["tests"]) > 0:
        test_code = top_tests["tests"][0]["code"]
        test_endpoint(
            f"Test Details ({test_code})",
            f"{BASE_URL}/analytics/tests/details/{test_code}?days=30"
        )

    # Test 6: Tests by Center
    test_endpoint(
        "Tests by Center (HVC)",
        f"{BASE_URL}/analytics/tests/by-center/HVC?days=30"
    )

    # Test 7: Test Categories
    test_endpoint(
        "Test Categories",
        f"{BASE_URL}/analytics/tests/categories?days=30"
    )

    # ========================================================================
    # SPECIES & BREEDS ANALYTICS
    # ========================================================================
    print("\n" + "=" * 70)
    print("SPECIES & BREEDS ANALYTICS")
    print("=" * 70)

    # Test 8: Species Distribution
    species_data = test_endpoint(
        "Species Distribution",
        f"{BASE_URL}/analytics/species/distribution?days=30"
    )

    # Test 9: Top Breeds
    top_breeds = test_endpoint(
        "Top Breeds (All Species)",
        f"{BASE_URL}/analytics/breeds/top?days=30&limit=10"
    )

    # Test 10: Top Breeds Filtered
    test_endpoint(
        "Top Breeds (Canino only)",
        f"{BASE_URL}/analytics/breeds/top?days=30&limit=10&species=Canino"
    )

    # Test 11: Species Profile by Center
    test_endpoint(
        "Species Profile (HVC)",
        f"{BASE_URL}/analytics/species/by-center/HVC?days=30"
    )

    # Test 12: Breed Details (if we have breed data)
    if top_breeds and top_breeds.get("breeds") and len(top_breeds["breeds"]) > 0:
        breed_name = top_breeds["breeds"][0]["breed"]
        test_endpoint(
            f"Breed Details ({breed_name})",
            f"{BASE_URL}/analytics/breeds/details/{breed_name}?days=30"
        )

    # ========================================================================
    # GLOBAL SUMMARY (ALL-IN-ONE)
    # ========================================================================
    print("\n" + "=" * 70)
    print("GLOBAL SUMMARY")
    print("=" * 70)

    # Test 13: Global Summary
    summary = test_endpoint(
        "Global Summary (All Analytics)",
        f"{BASE_URL}/analytics/summary?days=30"
    )

    if summary:
        print("\n[Summary Keys]:")
        for key in summary.keys():
            print(f"  - {key}")

    # ========================================================================
    # RESULTS SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print(f"\nTests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print(f"Total Tests: {tests_passed + tests_failed}")

    if tests_failed == 0:
        print("\n[SUCCESS] ALL ANALYTICS TESTS PASSED!")
        print("\nYou can now:")
        print(f"  - View API docs: {BASE_URL}/docs")
        print(f"  - Explore analytics: {BASE_URL}/analytics/summary")
        print(f"  - View dashboard: {BASE_URL}/")
    else:
        print(f"\n[WARNING] {tests_failed} tests failed")
        print("Check the error messages above")

    sys.exit(0 if tests_failed == 0 else 1)

except requests.exceptions.ConnectionError:
    print("\n[ERROR] Cannot connect to server")
    print("Make sure the server is running on http://localhost:8000")
    sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
