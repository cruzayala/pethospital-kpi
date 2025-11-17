# Local Testing Guide - PetHospital KPI

Esta guía te ayuda a probar el servicio KPI **localmente** antes de deployar a Railway.

## Pre-requisitos

- ✅ PostgreSQL 17 instalado y corriendo
- ✅ Python 3.11 o superior
- ✅ pethospital instalado localmente

---

## Paso 1: Iniciar Servicio KPI Local (5 minutos)

1. **Abre una terminal** en `pethospital-kpi`

2. **Ejecuta el script de testing**:
   ```bash
   test-local.bat
   ```

   Esto hará:
   - ✅ Crear base de datos `pethospital_kpi`
   - ✅ Crear entorno virtual Python
   - ✅ Instalar dependencias
   - ✅ Iniciar servidor en http://localhost:8000

3. **Verificar que inició correctamente**:
   - **Abre**: http://localhost:8000
   - **Deberías ver**: Dashboard KPI (vacío por ahora)
   - **Abre**: http://localhost:8000/docs
   - **Deberías ver**: API documentation (Swagger UI)

**Si ves errores**:
- Verifica que PostgreSQL esté corriendo
- Verifica que el puerto 8000 no esté ocupado
- Revisa los logs en la terminal

---

## Paso 2: Registrar Centro de Prueba (1 minuto)

1. **Deja el servicio KPI corriendo** (no cierres la terminal)

2. **Abre OTRA terminal** en `pethospital-kpi`

3. **Ejecuta**:
   ```bash
   register-center.bat
   ```

   Esto registra el centro HVC con API key `test-api-key-local-HVC-2025`

4. **Verificar**:
   - **Abre**: http://localhost:8000
   - **Deberías ver**: "Total Centers: 1"

---

## Paso 3: Configurar pethospital para Enviar Métricas (2 minutos)

1. **Edita** `pethospital/backend/.env`

2. **Agrega** (o actualiza) estas líneas al final:
   ```env
   # KPI Service Configuration (LOCAL TESTING)
   KPI_SERVICE_URL=http://localhost:8000
   CENTER_CODE=HVC
   CENTER_API_KEY=test-api-key-local-HVC-2025
   ```

3. **Guarda el archivo**

---

## Paso 4: Enviar Métricas de Prueba (2 minutos)

### Opción A: Usar Script (Recomendado)

1. **Abre terminal** en `pethospital`

2. **Ejecuta**:
   ```bash
   send-kpi-metrics.bat
   ```

   Deberías ver:
   ```
   Collecting metrics for 2025-11-16...
   Center: HVC

   Metrics Summary:
     Orders: 10
     Results: 8
     Pets: 5
     Tests: 3 types
     Species: 2 types

   Sending to http://localhost:8000...
   SUCCESS: Metrics sent for 2025-11-16
     Center: Hospital Veterinario Central
     Orders: 10
   ```

### Opción B: Test Manual con Curl

```bash
curl -X POST http://localhost:8000/kpi/submit \
  -H "Content-Type: application/json" \
  -d "{
    \"center_code\": \"HVC\",
    \"api_key\": \"test-api-key-local-HVC-2025\",
    \"date\": \"2025-11-17\",
    \"total_orders\": 15,
    \"total_results\": 12,
    \"total_pets\": 8,
    \"total_owners\": 7,
    \"tests\": [
      {\"code\": \"GLU\", \"name\": \"Glucosa\", \"count\": 5},
      {\"code\": \"BUN\", \"name\": \"Nitrogeno Ureico\", \"count\": 3}
    ],
    \"species\": [
      {\"species\": \"Canino\", \"count\": 5},
      {\"species\": \"Felino\", \"count\": 3}
    ],
    \"breeds\": [
      {\"breed\": \"Labrador\", \"species\": \"Canino\", \"count\": 2}
    ]
  }"
```

---

## Paso 5: Verificar Dashboard (1 minuto)

1. **Abre**: http://localhost:8000

2. **Verifica que muestre**:
   - ✅ Total Centers: 1
   - ✅ Active Centers: 1
   - ✅ Total Orders: (número que enviaste)
   - ✅ Total Results: (número que enviaste)
   - ✅ Gráfico de tendencia diaria con datos
   - ✅ Tabla de centros con "Hospital Veterinario Central"
   - ✅ Top Tests con tus pruebas
   - ✅ Species Distribution con tu distribución

**Si todo aparece correctamente: ✅ ¡El sistema funciona!**

---

## Paso 6: Probar API Endpoints (Opcional)

### Listar Centros
```bash
curl http://localhost:8000/kpi/centers
```

### Obtener Métricas de HVC
```bash
curl "http://localhost:8000/kpi/centers/HVC/metrics?days=30"
```

### Estadísticas Globales
```bash
curl "http://localhost:8000/kpi/stats/summary?days=30"
```

---

## Troubleshooting

### Error: "Cannot connect to database"
- **Causa**: PostgreSQL no está corriendo
- **Solución**: Inicia PostgreSQL: `net start postgresql-x64-17`

### Error: "Port 8000 is already in use"
- **Causa**: Otro proceso usa el puerto 8000
- **Solución**: Cambia el puerto en `test-local.bat` línea final: `--port 8001`

### Error: "Invalid center code or API key"
- **Causa**: Centro no registrado o API key incorrecta
- **Solución**: Ejecuta `register-center.bat` de nuevo

### Dashboard vacío después de enviar métricas
- **Causa**: Métricas enviadas con fecha muy antigua
- **Solución**: Envía métricas de hoy o ayer

### Script send_kpi_metrics.py no encuentra módulos
- **Causa**: No está en el entorno virtual de pethospital
- **Solución**:
  ```bash
  cd pethospital\backend
  call .venv\Scripts\activate
  cd ..
  python scripts\send_kpi_metrics.py
  ```

---

## Próximos Pasos

**Si todo funciona localmente:**

1. ✅ Commit cambios
2. ✅ Push a GitHub
3. ✅ Railway desplegará automáticamente
4. ✅ Repetir pasos 2-5 pero con URL de Railway

**Deploy a Railway:**
- Ver `RAILWAY_SETUP.md` para deployment paso a paso
- Usar API key diferente para producción (generar nueva)

---

## Comandos Rápidos

```bash
# Iniciar servicio KPI
test-local.bat

# Registrar centro (en otra terminal)
register-center.bat

# Enviar métricas desde pethospital
cd pethospital
send-kpi-metrics.bat

# Ver dashboard
# Abre navegador: http://localhost:8000

# Parar servicio
# Presiona Ctrl+C en la terminal del servicio KPI
```

---

## Base de Datos

**Conectar a la DB de pruebas**:
```bash
psql -U postgres -h localhost -d pethospital_kpi
```

**Ver datos**:
```sql
-- Centros registrados
SELECT * FROM centers;

-- Métricas diarias
SELECT * FROM daily_metrics ORDER BY date DESC;

-- Resumen de pruebas
SELECT * FROM test_summaries ORDER BY date DESC, count DESC;

-- Distribución de especies
SELECT * FROM species_summaries ORDER BY date DESC, count DESC;
```

**Limpiar datos de prueba**:
```sql
DELETE FROM breed_summaries;
DELETE FROM species_summaries;
DELETE FROM test_summaries;
DELETE FROM daily_metrics;
DELETE FROM centers WHERE code = 'HVC';
```

---

¡Listo! Con esto puedes probar todo localmente antes de subir a Railway.
