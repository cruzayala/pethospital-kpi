# Guía de Integración con Supabase

## ¿Cómo funciona el sistema actualmente?

Este sistema funciona con 2 componentes:

### 1. API de KPI (este proyecto)
- Recibe datos del software veterinario
- Almacena en PostgreSQL
- Muestra dashboard con gráficos

### 2. Software Veterinario (tu sistema principal)
- Envía datos al endpoint `/kpi/submit`
- Los datos incluyen: órdenes, resultados, mascotas, especies, razas, etc.

## Flujo de Datos

```
Software Veterinario → API /kpi/submit → PostgreSQL → Dashboard
```

El software veterinario **ENVÍA** los datos a esta API usando HTTP POST.

---

## Integración con Supabase

### Paso 1: Crear Proyecto en Supabase

1. Ve a https://supabase.com
2. Crea una cuenta (gratis)
3. Crea un nuevo proyecto
4. Anota tu password de la base de datos

### Paso 2: Obtener la URL de Conexión

1. En tu proyecto de Supabase, ve a **Settings** → **Database**
2. En la sección "Connection string", selecciona **URI**
3. Copia la URL, se verá así:
   ```
   postgresql://postgres.xxxxxxxx:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres
   ```
4. Reemplaza `[YOUR-PASSWORD]` con tu password real

### Paso 3: Crear las Tablas en Supabase

Ejecuta este script SQL en el **SQL Editor** de Supabase:

```sql
-- Tabla de Centros
CREATE TABLE centers (
    id SERIAL PRIMARY KEY,
    center_code VARCHAR(50) UNIQUE NOT NULL,
    center_name VARCHAR(200) NOT NULL,
    city VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de Métricas Diarias
CREATE TABLE daily_metrics (
    id SERIAL PRIMARY KEY,
    center_id INTEGER REFERENCES centers(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_orders INTEGER DEFAULT 0,
    total_results INTEGER DEFAULT 0,
    total_pets INTEGER DEFAULT 0,
    total_owners INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(center_id, date)
);

-- Tabla de Resumen de Pruebas
CREATE TABLE test_summary (
    id SERIAL PRIMARY KEY,
    center_id INTEGER REFERENCES centers(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    test_code VARCHAR(50) NOT NULL,
    test_name VARCHAR(200),
    count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(center_id, date, test_code)
);

-- Tabla de Resumen de Especies
CREATE TABLE species_summary (
    id SERIAL PRIMARY KEY,
    center_id INTEGER REFERENCES centers(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    species_name VARCHAR(100) NOT NULL,
    count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(center_id, date, species_name)
);

-- Tabla de Resumen de Razas
CREATE TABLE breed_summary (
    id SERIAL PRIMARY KEY,
    center_id INTEGER REFERENCES centers(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    breed VARCHAR(100) NOT NULL,
    species VARCHAR(100),
    count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(center_id, date, breed, species)
);

-- Crear índices para mejor rendimiento
CREATE INDEX idx_daily_metrics_center_date ON daily_metrics(center_id, date);
CREATE INDEX idx_test_summary_center_date ON test_summary(center_id, date);
CREATE INDEX idx_species_summary_center_date ON species_summary(center_id, date);
CREATE INDEX idx_breed_summary_center_date ON breed_summary(center_id, date);
```

### Paso 4: Configurar el Proyecto

1. **Copia el archivo de ejemplo:**
   ```bash
   copy .env.example .env
   ```

2. **Edita el archivo `.env` y actualiza la DATABASE_URL:**
   ```bash
   DATABASE_URL=postgresql://postgres.xxxxxxxx:[TU-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres
   ```

3. **Opcional - Configurar CORS para producción:**
   ```bash
   ALLOWED_ORIGINS=https://tu-dominio.com,https://otro-dominio.com
   ```

### Paso 5: Ejecutar las Migraciones

```bash
# Instalar alembic si no está instalado
pip install alembic

# Crear las tablas en Supabase
alembic upgrade head
```

### Paso 6: Reiniciar el Servidor

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Cómo Enviar Datos desde el Software Veterinario

Tu software veterinario debe hacer un **HTTP POST** al endpoint `/kpi/submit`.

### Ejemplo en Python:

```python
import requests
import datetime

# URL de tu API (puede estar en localhost, Railway, Vercel, etc.)
API_URL = "http://localhost:8000/kpi/submit"

# Datos a enviar
data = {
    "center_code": "HVC",
    "date": datetime.date.today().isoformat(),
    "orders": [
        {
            "order_id": "ORD-001",
            "pet_id": "PET-123",
            "owner_id": "OWN-456",
            "tests": [
                {"code": "GLU", "name": "Glucosa"},
                {"code": "BUN", "name": "Nitrógeno Ureico"}
            ]
        }
    ],
    "results": [
        {
            "result_id": "RES-001",
            "order_id": "ORD-001",
            "completed": True
        }
    ],
    "pets": [
        {
            "pet_id": "PET-123",
            "species": "Canino",
            "breed": "Golden Retriever"
        }
    ]
}

# Enviar datos
response = requests.post(API_URL, json=data)
print(response.json())
```

### Ejemplo en C# (.NET):

```csharp
using System.Net.Http;
using System.Text;
using System.Text.Json;

var client = new HttpClient();
var apiUrl = "http://localhost:8000/kpi/submit";

var data = new
{
    center_code = "HVC",
    date = DateTime.Now.ToString("yyyy-MM-dd"),
    orders = new[]
    {
        new
        {
            order_id = "ORD-001",
            pet_id = "PET-123",
            owner_id = "OWN-456",
            tests = new[]
            {
                new { code = "GLU", name = "Glucosa" },
                new { code = "BUN", name = "Nitrógeno Ureico" }
            }
        }
    },
    results = new[]
    {
        new { result_id = "RES-001", order_id = "ORD-001", completed = true }
    },
    pets = new[]
    {
        new { pet_id = "PET-123", species = "Canino", breed = "Golden Retriever" }
    }
};

var json = JsonSerializer.Serialize(data);
var content = new StringContent(json, Encoding.UTF8, "application/json");

var response = await client.PostAsync(apiUrl, content);
var result = await response.Content.ReadAsStringAsync();
Console.WriteLine(result);
```

---

## Opciones de Despliegue

### Opción 1: Local (Desarrollo)
- Base de datos: Supabase (en la nube)
- API: Tu computadora (localhost:8000)
- Dashboard: localhost:8000/

**Ventaja:** Fácil para desarrollo
**Desventaja:** Solo accesible desde tu computadora

### Opción 2: Railway.app (Recomendado)
- Base de datos: Supabase
- API + Dashboard: Railway (gratis con límites)
- URL pública automática

**Cómo desplegar en Railway:**
1. Ve a https://railway.app
2. Conecta tu repositorio de GitHub
3. Agrega la variable de entorno `DATABASE_URL` con la URL de Supabase
4. Railway te dará una URL pública tipo `https://tu-app.railway.app`

### Opción 3: Vercel / Render / Fly.io
Similares a Railway, también gratuitos con límites.

---

## Arquitectura Final

```
┌─────────────────────┐
│  Software Vet #1    │──┐
│  (Centro HVC)       │  │
└─────────────────────┘  │
                         │
┌─────────────────────┐  │    ┌──────────────────┐      ┌─────────────────┐
│  Software Vet #2    │──┼───→│  API FastAPI     │─────→│  Supabase       │
│  (Centro Cruz)      │  │    │  (Railway/Local) │      │  PostgreSQL     │
└─────────────────────┘  │    └──────────────────┘      └─────────────────┘
                         │             │
┌─────────────────────┐  │             │
│  Software Vet #3    │──┘             ↓
│  (Centro Esperanza) │         ┌──────────────────┐
└─────────────────────┘         │   Dashboard      │
                                │   (localhost/    │
                                │    Railway URL)  │
                                └──────────────────┘
```

**Flujo:**
1. Cada centro veterinario ejecuta tu software
2. Tu software envía datos diarios a la API (POST /kpi/submit)
3. La API guarda en Supabase (PostgreSQL en la nube)
4. El dashboard lee de Supabase y muestra gráficos
5. Cualquier persona con la URL del dashboard puede ver los KPIs

---

## Preguntas Frecuentes

### ¿Cómo llegan los datos a la base de datos?

Tu software veterinario debe **enviar** los datos usando HTTP POST.
No es que la API "consulte" tu software, es al revés: **tu software envía datos a la API**.

### ¿Cuándo se deben enviar los datos?

Tienes 3 opciones:

1. **Tiempo Real**: Cada vez que se crea una orden/resultado
2. **Cada Hora**: Un script que corre cada hora
3. **Fin del Día**: Un script que corre a las 11:59 PM

### ¿Qué pasa si envío datos duplicados?

La API está diseñada para manejar duplicados. Usa `UPSERT` (insert o update).
Si envías los datos del mismo día dos veces, se actualizan en lugar de duplicarse.

### ¿Es seguro?

Sí, puedes agregar:
- **Rate Limiting**: Ya configurado (100 requests/día por IP)
- **HTTPS**: Gratis con Railway/Vercel
- **Autenticación**: Puedes agregar API Keys si lo necesitas

### ¿Cuánto cuesta?

- **Supabase Free**: 500 MB de base de datos gratis (suficiente para miles de registros)
- **Railway Free**: $5 de crédito mensual gratis
- **Total**: $0/mes para empezar, escala según crezcas

---

## Próximos Pasos

1. ✅ Crear cuenta en Supabase
2. ✅ Obtener URL de conexión
3. ✅ Ejecutar script SQL para crear tablas
4. ✅ Actualizar `.env` con la URL de Supabase
5. ✅ Ejecutar migraciones: `alembic upgrade head`
6. ✅ Reiniciar servidor
7. ✅ Modificar tu software veterinario para enviar datos
8. ✅ Probar enviando datos de prueba
9. ⬜ (Opcional) Desplegar en Railway para tener URL pública

---

## Soporte

Si tienes dudas:
- Documentación de Supabase: https://supabase.com/docs
- Documentación de FastAPI: https://fastapi.tiangolo.com
- Railway Docs: https://docs.railway.app

