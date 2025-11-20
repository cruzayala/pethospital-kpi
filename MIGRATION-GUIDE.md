# Migration Guide: v1.0 → v2.0

Esta guía te ayudará a migrar tu instalación de PetHospital KPI Service de la versión 1.0 a la versión 2.0 (Production Ready).

---

## 📋 Pre-requisitos

Antes de comenzar la migración, asegúrate de tener:

- ✅ Acceso al servidor donde corre el servicio
- ✅ Backup de la base de datos (por si acaso)
- ✅ Acceso a las variables de entorno / archivo `.env`
- ✅ Python 3.11+ instalado
- ✅ 10-15 minutos de tiempo de inactividad planificado (opcional)

---

## 🚀 Paso 1: Backup

### Base de Datos

**Local (PostgreSQL)**:
```bash
pg_dump -U postgres pethospital_kpi > backup_v1_$(date +%Y%m%d).sql
```

**Railway**:
```bash
# Obtener DATABASE_URL desde Railway dashboard
pg_dump <DATABASE_URL> > backup_railway_v1_$(date +%Y%m%d).sql
```

### Código y Configuración

```bash
# Backup del archivo .env actual
cp .env .env.v1.backup

# Backup del código actual
git stash  # Si usas git
# o
cp -r app app.v1.backup
```

---

## 📦 Paso 2: Actualizar Dependencias

### Opción A: Usando Git (Recomendado)

```bash
# Pull los últimos cambios
git pull origin main

# Actualizar dependencias
pip install -r requirements.txt --upgrade
```

### Opción B: Manual

1. Actualiza `requirements.txt` con las nuevas dependencias:
```
# Agrega estas líneas al final
slowapi==0.1.9
passlib[bcrypt]==1.7.4
loguru==0.7.2
sentry-sdk[fastapi]==1.39.2
alembic==1.13.1
```

2. Instala las nuevas dependencias:
```bash
pip install -r requirements.txt
```

---

## ⚙️ Paso 3: Actualizar Variables de Entorno

### 3.1 Copiar Plantilla

```bash
# Guarda tu .env actual
cp .env .env.old

# Usa la nueva plantilla como base
cp .env.example .env
```

### 3.2 Migrar Configuración Existente

Copia estas variables de tu `.env.old`:
- `DATABASE_URL`
- `PORT`

### 3.3 Configurar Nuevas Variables Obligatorias

Edita `.env` y configura:

```bash
# =============================================================================
# SECURITY CONFIGURATION (NUEVAS - OBLIGATORIAS)
# =============================================================================

# CORS - Dominios permitidos (IMPORTANTE PARA PRODUCCIÓN)
# Para desarrollo, puedes usar *
# Para producción, especifica tus dominios
ALLOWED_ORIGINS=https://tu-dominio-codex.com,https://otro-dominio.com
# o para desarrollo:
# ALLOWED_ORIGINS=*

# Dashboard Authentication (NUEVO - OBLIGATORIO)
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=TU_PASSWORD_SEGURA_AQUI_123!

# =============================================================================
# RATE LIMITING (NUEVAS - OPCIONALES)
# =============================================================================
RATE_LIMIT_SUBMIT=100/day
RATE_LIMIT_EVENTS=1000/day
RATE_LIMIT_DASHBOARD=60/minute

# =============================================================================
# MONITORING & LOGGING (NUEVAS - OPCIONALES)
# =============================================================================

# Sentry (Opcional - para error tracking)
# Obtén tu DSN en https://sentry.io
SENTRY_DSN=

# Ambiente (development, staging, production)
ENVIRONMENT=production

# Nivel de logs
LOG_LEVEL=INFO

# =============================================================================
# APPLICATION SETTINGS (NUEVAS - OPCIONALES)
# =============================================================================
APP_TITLE=PetHospital KPI Service
APP_VERSION=2.0.0
ENABLE_DOCS=true  # Cambia a false en producción si quieres ocultar /docs
```

---

## 🔑 Paso 4: Actualizar Clientes API (Codex Installations)

Los sistemas Codex que envían métricas deben ser actualizados para usar el header `X-API-Key`.

### Antes (v1.0):
```python
# Python example
response = requests.post(
    "https://kpi-service.com/kpi/submit",
    json={
        "center_code": "HVC",
        "api_key": "test-api-key-local-HVC-2025",  # ❌ Deprecated
        "date": "2025-11-19",
        "total_orders": 50,
        # ...
    }
)
```

### Después (v2.0):
```python
# Python example
response = requests.post(
    "https://kpi-service.com/kpi/submit",
    headers={
        "X-API-Key": "test-api-key-local-HVC-2025"  # ✅ Recomendado
    },
    json={
        "center_code": "HVC",
        "date": "2025-11-19",
        "total_orders": 50,
        # ...
    }
)
```

### C# Example:
```csharp
// Antes (v1.0)
var data = new {
    center_code = "HVC",
    api_key = "test-api-key-local-HVC-2025",  // ❌ Deprecated
    date = "2025-11-19",
    total_orders = 50
};

// Después (v2.0)
var client = new HttpClient();
client.DefaultRequestHeaders.Add("X-API-Key", "test-api-key-local-HVC-2025");  // ✅

var data = new {
    center_code = "HVC",
    date = "2025-11-19",
    total_orders = 50
};
var response = await client.PostAsJsonAsync("https://kpi-service.com/kpi/submit", data);
```

### cURL Example:
```bash
# Antes (v1.0)
curl -X POST https://kpi-service.com/kpi/submit \
  -H "Content-Type: application/json" \
  -d '{
    "center_code": "HVC",
    "api_key": "test-api-key-local-HVC-2025",
    "date": "2025-11-19",
    "total_orders": 50
  }'

# Después (v2.0)
curl -X POST https://kpi-service.com/kpi/submit \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key-local-HVC-2025" \
  -d '{
    "center_code": "HVC",
    "date": "2025-11-19",
    "total_orders": 50
  }'
```

**NOTA IMPORTANTE**: La versión 2.0 sigue aceptando API keys en el body por retrocompatibilidad, pero esto será removido en v3.0.

---

## 🔄 Paso 5: Reiniciar el Servicio

### Local (Development):

```bash
# Detener el servicio actual (Ctrl+C)

# Reiniciar con la nueva versión
python -m uvicorn app.main:app --reload
# o
.\run-kpi-service.bat  # Windows
```

### Railway (Production):

Railway auto-desplegará cuando hagas push:

```bash
git add .
git commit -m "Upgrade to v2.0 - Production Ready"
git push origin main
```

### Verificar Reinicio:

```bash
# Check health
curl https://tu-kpi-service.com/health

# Debería responder:
# {
#   "status": "ok",
#   "service": "PetHospital KPI Service",
#   "version": "2.0.0",
#   "environment": "production"
# }
```

---

## ✅ Paso 6: Verificar Funcionamiento

### 6.1 Verificar Health Checks

```bash
# Liveness
curl https://tu-kpi-service.com/health

# Readiness (verifica BD)
curl https://tu-kpi-service.com/health/ready
```

### 6.2 Verificar Dashboard

```bash
# Accede al dashboard en tu navegador
https://tu-kpi-service.com/

# Deberías ver un prompt de autenticación
# Username: [tu DASHBOARD_USERNAME]
# Password: [tu DASHBOARD_PASSWORD]
```

### 6.3 Verificar Envío de Métricas

```bash
# Test con curl
curl -X POST https://tu-kpi-service.com/kpi/submit \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu-api-key-aqui" \
  -d '{
    "center_code": "HVC",
    "date": "2025-11-19",
    "total_orders": 10,
    "total_results": 8,
    "total_pets": 5,
    "total_owners": 4,
    "tests": [],
    "species": [],
    "breeds": []
  }'

# Debería responder 201 Created
```

### 6.4 Verificar Rate Limiting

```bash
# Intenta hacer muchas requests rápidas
for i in {1..150}; do
  curl -X POST https://tu-kpi-service.com/kpi/submit \
    -H "X-API-Key: tu-key" \
    -H "Content-Type: application/json" \
    -d '{"center_code":"HVC","date":"2025-11-19","total_orders":1}'
done

# Deberías recibir 429 Too Many Requests después de 100 requests
```

### 6.5 Verificar Logs

```bash
# Local
cat logs/kpi-service_2025-11-19.log

# Railway
# Ve a tu Railway dashboard → Service → Logs
```

---

## 📊 Paso 7: Monitoreo (Opcional)

### Configurar Sentry

1. Crea una cuenta en https://sentry.io (gratis para proyectos pequeños)
2. Crea un nuevo proyecto → Python → FastAPI
3. Copia tu DSN
4. Agrégalo a `.env`:
```
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
```
5. Reinicia el servicio
6. Verifica en Sentry dashboard que aparezcan eventos

---

## 🚨 Troubleshooting

### Problema: "Configuration validation failed: DASHBOARD_PASSWORD must be changed"

**Solución**: Cambia `DASHBOARD_PASSWORD` en tu `.env` a un password seguro.

---

### Problema: "Invalid center code or API key" después de migrar

**Causa**: Estás enviando el API key en el body pero el servidor espera el header.

**Solución Temporal**:
- La v2.0 sigue aceptando API key en el body por retrocompatibilidad
- Verifica que estés enviando el header `Content-Type: application/json`

**Solución Permanente**:
- Actualiza tu cliente para usar `X-API-Key` header

---

### Problema: "429 Too Many Requests"

**Causa**: Has excedido el rate limit configurado.

**Solución**:
1. Espera a que se resetee el contador (1 día para `/submit`, 1 minuto para dashboard)
2. O aumenta los límites en `.env`:
```
RATE_LIMIT_SUBMIT=500/day  # Aumenta de 100 a 500
```

---

### Problema: Dashboard pide usuario/contraseña pero no los tengo

**Causa**: No configuraste `DASHBOARD_USERNAME` y `DASHBOARD_PASSWORD`.

**Solución**:
1. Edita `.env` y agrega:
```
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=tu-password-aqui
```
2. Reinicia el servicio

---

### Problema: CORS error en el navegador

**Error**: `Access to XMLHttpRequest has been blocked by CORS policy`

**Causa**: Tu dominio no está en `ALLOWED_ORIGINS`.

**Solución**:
1. Edita `.env`:
```
ALLOWED_ORIGINS=https://tu-dominio.com,https://otro-dominio.com
```
2. Reinicia el servicio

---

### Problema: Database connection error

**Error**: `Database Connection Error (503)`

**Causa**:
- Base de datos no disponible
- DATABASE_URL incorrecto

**Solución**:
1. Verifica que PostgreSQL esté corriendo
2. Verifica DATABASE_URL en `.env`
3. Para Railway, verifica que el servicio de PostgreSQL esté activo

---

## 📝 Rollback (Si algo sale mal)

### Rollback Local:

```bash
# 1. Detener servicio actual
Ctrl+C

# 2. Restaurar código anterior
git checkout v1.0  # Si usas git
# o
rm -rf app && mv app.v1.backup app

# 3. Restaurar .env
cp .env.v1.backup .env

# 4. Reinstalar dependencias viejas
pip install -r requirements.txt

# 5. Reiniciar
python -m uvicorn app.main:app --reload
```

### Rollback Railway:

```bash
# En Railway dashboard:
# 1. Ve a Deployments
# 2. Encuentra el deployment anterior (v1.0)
# 3. Click en "Redeploy"
```

### Rollback Base de Datos (si es necesario):

```bash
# Solo si hiciste cambios en el schema (en v2.0 no hay cambios)
psql -U postgres pethospital_kpi < backup_v1_YYYYMMDD.sql
```

---

## 📞 Soporte

Si tienes problemas durante la migración:

1. **Revisa los logs**: `logs/kpi-service_*.log` o Railway dashboard
2. **Consulta el CHANGELOG**: [CHANGELOG.md](CHANGELOG.md)
3. **Abre un issue**: [GitHub Issues](https://github.com/your-org/pethospital-kpi/issues)
4. **Contacta**: support@your-domain.com

---

## ✅ Checklist Final

- [ ] Backup de base de datos completado
- [ ] Backup de código y `.env` completado
- [ ] Dependencias actualizadas
- [ ] Variables de entorno configuradas (especialmente DASHBOARD_PASSWORD)
- [ ] CORS configurado para producción
- [ ] Servicio reiniciado exitosamente
- [ ] Health checks respondiendo correctamente
- [ ] Dashboard accesible con autenticación
- [ ] Clientes API actualizados para usar `X-API-Key` header (o planificado)
- [ ] Logs funcionando correctamente
- [ ] Rate limiting verificado
- [ ] Sentry configurado (opcional)
- [ ] Documentación actualizada para tu equipo

---

## 🎉 ¡Migración Completada!

Felicidades, tu PetHospital KPI Service ahora está en la versión 2.0 Production-Ready con:

- ✅ Seguridad mejorada (CORS, Auth, Rate Limiting)
- ✅ Logging estructurado
- ✅ Monitoreo de errores (Sentry)
- ✅ Health checks mejorados
- ✅ Mejor manejo de errores

Tu servicio está listo para producción. 🚀
