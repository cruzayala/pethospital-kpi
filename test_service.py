"""
Script de prueba para verificar que el servicio KPI está funcionando correctamente
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test del endpoint /health"""
    print("\n=== Test /health ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    print("✅ Health check passed!")

def test_health_ready():
    """Test del endpoint /health/ready"""
    print("\n=== Test /health/ready ===")
    response = requests.get(f"{BASE_URL}/health/ready")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Readiness check passed!")

def test_api_docs_info():
    """Test del endpoint /api/docs-info"""
    print("\n=== Test /api/docs-info ===")
    response = requests.get(f"{BASE_URL}/api/docs-info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ API docs info passed!")

def test_centers_list():
    """Test del endpoint /kpi/centers"""
    print("\n=== Test /kpi/centers ===")
    response = requests.get(f"{BASE_URL}/kpi/centers")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Centers list passed!")

def test_dashboard_auth():
    """Test que el dashboard requiere autenticación"""
    print("\n=== Test Dashboard Authentication ===")

    # Sin auth - debe fallar
    response = requests.get(f"{BASE_URL}/")
    print(f"Status without auth: {response.status_code}")
    assert response.status_code == 401
    print("✅ Dashboard correctly requires authentication!")

    # Con auth - debe funcionar
    response = requests.get(f"{BASE_URL}/", auth=("admin", "change-this-secure-password"))
    print(f"Status with auth: {response.status_code}")
    assert response.status_code == 200
    print("✅ Dashboard accessible with correct credentials!")

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING PETHOSPITAL KPI SERVICE v2.0")
    print("=" * 60)

    try:
        test_health()
        test_health_ready()
        test_api_docs_info()
        test_centers_list()
        test_dashboard_auth()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nEl servicio está funcionando correctamente.")
        print("Puedes acceder a:")
        print(f"  - Dashboard: {BASE_URL}/ (usuario: admin, password: change-this-secure-password)")
        print(f"  - API Docs: {BASE_URL}/docs")
        print(f"  - Health: {BASE_URL}/health")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se puede conectar al servidor")
        print("Asegúrate de que el servidor esté corriendo en http://localhost:8000")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
