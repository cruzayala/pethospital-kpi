# coding: utf-8
"""
Test final del servicio KPI v2.0
Prueba que todo funciona sin autenticacion en el dashboard
"""
import sys
import requests

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("TEST FINAL - PETHOSPITAL KPI SERVICE v2.0")
print("=" * 60)

try:
    # Test 1: Health Check
    print("\n[Test 1] Health Check...")
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    assert r.status_code == 200
    print(f"[OK] Health: {r.json()}")

    # Test 2: Readiness Check
    print("\n[Test 2] Readiness Check...")
    r = requests.get(f"{BASE_URL}/health/ready", timeout=5)
    assert r.status_code == 200
    print(f"[OK] Readiness: {r.json()}")

    # Test 3: Dashboard SIN autenticacion
    print("\n[Test 3] Dashboard (sin autenticacion)...")
    r = requests.get(f"{BASE_URL}/", timeout=10)
    if r.status_code == 200:
        print(f"[OK] Dashboard accesible sin autenticacion!")
        print(f"[OK] Longitud HTML: {len(r.text)} caracteres")
    else:
        print(f"[ERROR] Dashboard status: {r.status_code}")
        print(f"[ERROR] Aun requiere autenticacion")
        sys.exit(1)

    # Test 4: API Docs
    print("\n[Test 4] API Docs...")
    r = requests.get(f"{BASE_URL}/docs", timeout=5)
    assert r.status_code == 200
    print(f"[OK] API Docs accesible")

    # Test 5: Centros
    print("\n[Test 5] Lista de centros...")
    r = requests.get(f"{BASE_URL}/kpi/centers", timeout=5)
    assert r.status_code == 200
    centers = r.json()
    print(f"[OK] Centros registrados: {len(centers)}")
    for center in centers:
        print(f"     - {center['code']}: {center['name']}")

    print("\n" + "=" * 60)
    print("[EXITO] TODOS LOS TESTS PASARON!")
    print("=" * 60)
    print("\nEl servicio esta funcionando correctamente.")
    print("\nPuedes acceder a:")
    print(f"  - Dashboard: {BASE_URL}/")
    print(f"  - API Docs: {BASE_URL}/docs")
    print(f"  - Health: {BASE_URL}/health")
    print("\n[IMPORTANTE] Dashboard ahora es PUBLICO (sin autenticacion)")

except AssertionError as e:
    print(f"\n[ERROR] Test fallo: {e}")
    sys.exit(1)
except requests.exceptions.Timeout:
    print("\n[ERROR] Timeout - El servidor tarda demasiado en responder")
    sys.exit(1)
except requests.exceptions.ConnectionError:
    print("\n[ERROR] No se puede conectar al servidor")
    print("Asegurate de que el servidor este corriendo en http://localhost:8000")
    sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] Inesperado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
