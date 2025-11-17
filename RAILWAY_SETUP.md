# Railway Setup Guide - Paso a Paso

Esta guía te ayudará a deployar el servicio KPI en Railway completamente GRATIS.

## Paso 1: Crear Cuenta en Railway

1. Ve a https://railway.app
2. Click en "Login" (arriba derecha)
3. Selecciona "Login with GitHub"
4. Autoriza Railway para acceder a tu GitHub
5. ✅ Cuenta creada! Tienes $5 de crédito gratis cada mes

## Paso 2: Crear Repositorio en GitHub

1. Ve a GitHub y crea un nuevo repositorio llamado `pethospital-kpi`
2. Inicializa este proyecto con git:

```bash
cd pethospital-kpi
git init
git add .
git commit -m "Initial commit: KPI service for Railway"
git remote add origin https://github.com/TU-USUARIO/pethospital-kpi.git
git push -u origin main
```

## Paso 3: Deploy en Railway

1. En Railway dashboard, click "New Project"
2. Select "Deploy from GitHub repo"
3. Selecciona el repo `pethospital-kpi`
4. Railway detectará automáticamente que es Python/FastAPI
5. Click "Deploy Now"

⏳ Railway instalará dependencias y desplegará automáticamente (2-3 minutos)

## Paso 4: Agregar PostgreSQL

1. En tu proyecto, click "+ New"
2. Select "Database"
3. Click "Add PostgreSQL"
4. ✅ Railway crea la base de datos y configura DATABASE_URL automáticamente

## Paso 5: Verificar el Deploy

1. En Railway, click en tu servicio
2. Click en "Settings" → "Networking"
3. Copia la URL pública (algo como: `https://pethospital-kpi-production.up.railway.app`)
4. Abre esa URL en tu navegador
5. Deberías ver el dashboard (vacío por ahora)

## Paso 6: Registrar tu Centro

Necesitas agregar tu centro a la base de datos:

### Opción A: Usar Railway PostgreSQL GUI

1. En Railway, click en tu base de datos PostgreSQL
2. Click en "Data" tab
3. Ejecuta este SQL:

```sql
-- Generar API key primero (usa Python local o generador online)
-- import secrets; print(secrets.token_urlsafe(32))

INSERT INTO centers (code, name, country, city, api_key, is_active, registered_at)
VALUES (
  'HVC',  -- Tu código de centro
  'Hospital Veterinario Central',  -- Nombre de tu centro
  'Republica Dominicana',
  'Santo Domingo',
  'TU-API-KEY-AQUI',  -- Genera una key segura
  1,
  NOW()
);
```

### Opción B: Conectar con psql local

```bash
# Railway te da esta URL en "Connect" tab
psql postgresql://postgres:password@region.railway.internal:5432/railway

# Luego ejecuta el INSERT de arriba
```

## Paso 7: Generar API Key

Ejecuta esto en Python local:

```python
import secrets
api_key = secrets.token_urlsafe(32)
print(f"Tu API key: {api_key}")
# Guarda esta key en lugar seguro!
```

## Paso 8: Configurar Codex Local

Agrega estas variables al archivo `backend/.env` de tu instalación Codex:

```bash
# KPI Service Configuration
KPI_SERVICE_URL=https://tu-app.up.railway.app
CENTER_CODE=HVC  # Tu código de centro
CENTER_API_KEY=la-api-key-que-generaste
```

## Paso 9: Test de Envío

Prueba enviar métricas desde tu instalación local:

```bash
# Windows
cd pethospital
send-kpi-metrics.bat

# Linux/Mac
python scripts/send_kpi_metrics.py
```

Deberías ver:
```
SUCCESS: Metrics sent for 2025-11-12
  Center: Hospital Veterinario Central
  Orders: 50
```

## Paso 10: Verificar Dashboard

1. Abre tu URL de Railway en el navegador
2. Deberías ver:
   - 1 centro registrado
   - Estadísticas del día que enviaste
   - Gráficos con datos

## Automatizar Envío Diario

### Windows: Task Scheduler

1. Abre "Task Scheduler" (Programador de Tareas)
2. Click "Create Basic Task"
3. Nombre: "Send KPI Metrics"
4. Trigger: "Daily" a las 00:30 AM
5. Action: "Start a program"
6. Program: `C:\ruta\completa\send-kpi-metrics.bat`
7. Finish!

### Linux/Mac: Cron Job

```bash
# Editar crontab
crontab -e

# Agregar esta línea (ejecuta a las 00:30 AM diario)
30 0 * * * cd /path/to/pethospital && python scripts/send_kpi_metrics.py
```

## Monitoreo

### Ver Logs en Railway

1. Click en tu servicio
2. Click "Deployments"
3. Click en el deployment activo
4. Click "View Logs"

### Métricas de Uso

1. Click "Metrics" tab
2. Verás:
   - CPU usage
   - Memory usage
   - Network traffic

### Estimado de Costos

Con 5 centros enviando 1 vez al día:
- Requests: ~150/mes
- Database: ~10MB
- Bandwidth: <100MB

**Total: $0.00 (gratis con el plan free)**

## Troubleshooting

### Error: "Invalid center code or API key"

- Verifica que CENTER_CODE en .env coincida con el `code` en la DB
- Verifica que CENTER_API_KEY sea correcto

### Error: "Cannot connect to KPI service"

- Verifica que KPI_SERVICE_URL esté correcto en .env
- Verifica que el servicio esté running en Railway

### El dashboard está vacío

- Verifica que hayas ejecutado send-kpi-metrics.bat
- Verifica en Railway logs que recibió el POST

### Database error

- Asegúrate que PostgreSQL está agregado en Railway
- Verifica que DATABASE_URL exista en variables de entorno

## Agregar Más Centros

Para cada centro adicional:

1. Instala Codex en el nuevo centro
2. Agrega el centro a la DB (mismo SQL de arriba, diferente code)
3. Genera nueva API key para ese centro
4. Configura .env en ese centro con su API key
5. Programa send-kpi-metrics.bat en ese centro

## Seguridad

✅ **Datos seguros:**
- API keys únicas por centro
- Solo métricas agregadas (no datos sensibles)
- HTTPS en Railway
- Database no expuesta públicamente

⚠️ **Nunca compartas:**
- API keys
- DATABASE_URL de Railway
- Credenciales de Railway

## Soporte

Si algo no funciona:
1. Revisa los logs en Railway
2. Verifica las variables de entorno
3. Prueba el endpoint manualmente con Postman/curl
4. Revisa el README.md

## Next Steps

Una vez funcionando:
1. Agrega más centros
2. Personaliza el dashboard (templates/dashboard.html)
3. Agrega alertas por email (opcional)
4. Exporta reportes PDF (opcional)

¡Listo! Tu sistema KPI está corriendo en Railway gratis 🎉
