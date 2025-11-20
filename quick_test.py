import sys
try:
    import requests
    print("[OK] Modulo requests disponible")

    # Test rapido
    r = requests.get("http://localhost:8000/health", timeout=2)
    print(f"[OK] Servidor responde! Status: {r.status_code}")
    print(f"Respuesta: {r.json()}")
except ImportError:
    print("[ERROR] Modulo 'requests' no instalado")
    print("Instalar con: pip install requests")
    sys.exit(1)
except requests.exceptions.ConnectionError:
    print("[ERROR] No se puede conectar al servidor en http://localhost:8000")
    print("Asegurate de que el servidor este corriendo")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR]: {e}")
    sys.exit(1)
