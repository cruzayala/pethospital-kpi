# Codex Veterinaria - KPI Service Launcher

## 🚀 Inicio Rápido

### Opción 1: Solo KPI Service
Hacer doble clic en:
```
run-kpi-service.bat
```

### Opción 2: Sistema Completo (KPI + Backend)
Desde la carpeta HVC/, hacer doble clic en:
```
iniciar-codex-con-kpi.bat
```

## 📋 ¿Qué hace cada launcher?

### `run-kpi-service.bat`
- Verifica que Python esté instalado
- Crea el entorno virtual (.venv) si no existe
- Instala dependencias automáticamente
- Inicia el servicio KPI en puerto 8000
- Muestra logs en tiempo real

**Puertos**:
- KPI Service: `http://localhost:8000`
- Documentación API: `http://localhost:8000/docs`

### `iniciar-codex-con-kpi.bat` (en carpeta HVC/)
- Inicia KPI Service (ventana 1)
- Espera 5 segundos
- Inicia Backend PetHospital (ventana 2)
- Muestra resumen de servicios iniciados

**Puertos**:
- KPI Service: `http://localhost:8000`
- Backend API: `http://localhost:8010`

## ✅ Verificar que funciona

### 1. Verificar KPI Service
Abrir navegador en: `http://localhost:8000/health`

Debería mostrar:
```json
{"status": "healthy", "service": "kpi-tracker"}
```

### 2. Verificar integración con Backend
Abrir navegador en: `http://localhost:8000/kpi/centers`

Debería mostrar lista de centros registrados con metadata completa.

### 3. Ver logs del Backend
En la terminal del Backend, buscar:
```
[startup] Registering X centers with KPI service...
[startup] Successfully registered X/X centers with KPI
```

## 🔧 Solución de Problemas

### Error: "Python is not installed"
Instalar Python 3.8+ desde: https://www.python.org/downloads/

### Error: "Failed to install dependencies"
Ejecutar manualmente:
```bash
cd pethospital-kpi
python -m venv .venv
.venv\Scripts\pip.exe install -r requirements.txt
```

### Puerto 8000 ya está en uso
Matar proceso:
```bash
netstat -ano | findstr :8000
taskkill /F /PID <process_id>
```

### KPI Service no recibe datos
1. Verificar que Backend tiene estas variables en `.env`:
   ```
   KPI_TRACKING_ENABLED=true
   KPI_SERVICE_URL=http://localhost:8000
   CENTER_API_KEY=test-api-key-local-HVC-2025
   ```

2. Reiniciar Backend después de iniciar KPI

## 📊 Endpoints Disponibles

### KPI Service (puerto 8000)

- `GET /health` - Estado del servicio
- `GET /kpi/centers` - Lista centros registrados
- `POST /kpi/events` - Recibir eventos (usado por Backend)
- `POST /kpi/submit` - Enviar métricas diarias
- `GET /kpi/stats/summary` - Resumen de estadísticas
- `GET /docs` - Documentación interactiva (Swagger)

## 🔄 Flujo de Integración

1. **Startup**: Backend registra todos los centros en KPI
2. **Create/Update**: Cambios en centros se sincronizan automáticamente
3. **Events**: Scanner envía eventos cada 60 segundos
4. **Metrics**: KPI calcula y almacena estadísticas

## 📝 Archivos Importantes

- `run-kpi-service.bat` - Launcher del servicio KPI
- `app/main.py` - Aplicación FastAPI
- `app/routes/kpi.py` - Endpoints del API
- `app/models.py` - Modelos de base de datos
- `requirements.txt` - Dependencias Python
- `.env` (crear si no existe) - Variables de entorno

## 🎯 Uso en Producción

Para producción, usar:
```bash
.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

O configurar como servicio de Windows con NSSM.

---

**Versión**: 1.0
**Fecha**: 2025-11-18
**Soporte**: Para problemas, revisar logs en terminal
