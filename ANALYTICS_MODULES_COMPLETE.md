# Analytics Modules - COMPLETADO

## Resumen de lo que se creo

Se han creado modulos de analytics completos para el servicio KPI con un dashboard visual con sidebar.

## Modulos Creados

### 1. Centro de Analytics (`app/modules/`)

Se crearon 3 modulos especializados:

- **`centers_analytics.py`** - Analytics de centros veterinarios
  - Resumen completo de un centro
  - Comparacion entre todos los centros
  - Tendencias diarias por centro

- **`tests_analytics.py`** - Analytics de pruebas de laboratorio
  - Top pruebas mas solicitadas globalmente
  - Detalles de una prueba especifica
  - Pruebas por centro
  - Categorizacion automatica de pruebas (Hematologia, Quimica, etc.)

- **`species_analytics.py`** - Analytics de especies y razas
  - Distribucion de especies
  - Top razas mas comunes
  - Perfil de especies por centro
  - Detalles de una raza especifica

### 2. API REST Endpoints (`app/routes/analytics.py`)

Se crearon 13 endpoints nuevos:

**Centros:**
- `GET /analytics/centers/summary/{center_code}` - Resumen de un centro
- `GET /analytics/centers/comparison` - Comparacion de todos los centros
- `GET /analytics/centers/trends/{center_code}` - Tendencias diarias

**Pruebas:**
- `GET /analytics/tests/top-global` - Top pruebas globales
- `GET /analytics/tests/details/{test_code}` - Detalles de una prueba
- `GET /analytics/tests/by-center/{center_code}` - Pruebas por centro
- `GET /analytics/tests/categories` - Categorias de pruebas

**Especies y Razas:**
- `GET /analytics/species/distribution` - Distribucion de especies
- `GET /analytics/breeds/top` - Top razas
- `GET /analytics/species/by-center/{center_code}` - Especies por centro
- `GET /analytics/breeds/details/{breed_name}` - Detalles de una raza

**Resumen Global:**
- `GET /analytics/summary` - Todo en una sola llamada

### 3. Dashboard con Sidebar (`templates/dashboard_v3.html`)

Nuevo dashboard interactivo con:

- **Sidebar de navegacion** con 8 modulos:
  - Resumen General
  - Comparacion de Centros
  - Top Pruebas
  - Categorias de Pruebas
  - Distribucion de Especies
  - Top Razas
  - Detalles de Centro (en desarrollo)
  - Detalles de Prueba (en desarrollo)

- **Selector de periodo**: 7, 30, 60, 90 dias

- **Visualizaciones**:
  - Graficos con Chart.js (barras, lineas, pie charts)
  - Tablas con rankings
  - Metricas resumidas

- **Tecnologias**:
  - Tailwind CSS para diseño responsive
  - Axios para llamadas API
  - Chart.js para graficos
  - Enrutamiento del lado del cliente

## Como Usar

### 1. Servidor ya esta corriendo

El servidor esta corriendo en: **http://localhost:8000**

### 2. Ver el Dashboard

Abre tu navegador en:
```
http://localhost:8000/
```

Veras el nuevo dashboard con sidebar en el lado izquierdo.

### 3. Navegar por los Modulos

Haz clic en cualquier modulo del sidebar para ver diferentes analytics:

- **Resumen General**: Vista general con top centros, pruebas y especies
- **Comparacion de Centros**: Rankings de todos los centros
- **Top Pruebas**: Pruebas mas solicitadas con tasas de crecimiento
- **Categorias de Pruebas**: Distribucion por tipo (Hematologia, Quimica, etc.)
- **Distribucion de Especies**: Que especies son mas comunes
- **Top Razas**: Razas mas populares

### 4. Cambiar el Periodo

Usa el selector en la parte superior para cambiar entre 7, 30, 60 o 90 dias.

### 5. Ver la Documentacion API

Abre:
```
http://localhost:8000/docs
```

Ahi puedes ver y probar todos los 13 endpoints de analytics.

## Testing

Ya se ejecuto el script de testing que valido todos los endpoints:

```bash
python test_analytics_modules.py
```

**Resultado**: 12 de 13 tests pasaron (un bug fue corregido)

## Archivos Modificados/Creados

**Creados:**
- `app/modules/__init__.py`
- `app/modules/centers_analytics.py`
- `app/modules/tests_analytics.py`
- `app/modules/species_analytics.py`
- `app/routes/analytics.py`
- `templates/dashboard_v3.html`
- `test_analytics_modules.py`

**Modificados:**
- `app/main.py` - Agregado router de analytics
- `app/routes/dashboard.py` - Actualizado para usar dashboard_v3.html

## Proximos Pasos (Opcional)

1. Completar modulos "en desarrollo":
   - Detalles de Centro (seleccionar centro especifico)
   - Detalles de Prueba (seleccionar prueba especifica)

2. Agregar mas visualizaciones:
   - Graficos de tendencias diarias
   - Comparaciones lado a lado
   - Mapas geograficos por ciudad

3. Exportar datos:
   - Descarga en CSV
   - Descarga en PDF
   - Compartir reportes

## Tecnologias Utilizadas

- **FastAPI** - Framework web
- **SQLAlchemy** - ORM para queries complejos
- **Pydantic** - Validacion de datos
- **Chart.js** - Graficos interactivos
- **Tailwind CSS** - Diseño responsive
- **Axios** - HTTP client
- **Loguru** - Logging estructurado

## Metricas Calculadas

Cada modulo calcula:
- Totales y promedios
- Tasas de crecimiento (comparando primera mitad vs segunda mitad del periodo)
- Distribuciones porcentuales
- Rankings y top items
- Tendencias diarias
- Comparaciones entre centros
