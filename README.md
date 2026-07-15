# Cruz Morada - API de Estadísticas de Ventas

Servicio REST desarrollado con **Python** y **FastAPI** que procesa un archivo CSV de gran volumen (~3.2 millones de registros) con datos de ventas de la cadena de farmacias Cruz Morada, y expone endpoints para consultar estadísticas con filtros dinámicos.

## Características

- **Carga desatendida**: El CSV se procesa automáticamente al iniciar la aplicación.
- **Procesamiento paralelo**: Usa `concurrent.futures.ProcessPoolExecutor` con chunking para cargar el CSV en ~8-10 segundos.
- **Filtros dinámicos**: Soporta filtros por género, edad, canal, código de producto, ID de persona, local y rango de fechas.
- **Documentación Swagger**: Disponible en `/docs` (Swagger UI) y `/redoc` (ReDoc).
- **Manejo de errores estándar**: Respuestas de error con formato consistente (RFC 7807).

## Requisitos

- Python 3.10+
- pip

## Instalación

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd cruz-morada-3

# Instalar dependencias
pip install -r requirements.txt
```

## Ejecución

```bash
# Iniciar el servidor
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Al iniciar, la aplicación cargará automáticamente el archivo `ventas_completas.csv` desde la raíz del proyecto. Verás en los logs el progreso de la carga:

```
2026-07-14 19:07:28 [INFO] Iniciando carga del CSV...
2026-07-14 19:07:28 [INFO] Configuración: chunk_size=100000, max_workers=4
2026-07-14 19:07:37 [INFO] Carga completada: 3242878 filas en 8.20 segundos
```

Una vez cargado, el servidor estará disponible en:

- **API**: http://127.0.0.1:8000
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Endpoints

### Base URL

```
/v1/estadisticas/ventas
```

### GET - Estadísticas con filtros por query params

Devuelve estadísticas de ventas. Sin parámetros retorna estadísticas globales.

**Ejemplo sin filtros:**

```bash
curl http://127.0.0.1:8000/v1/estadisticas/ventas
```

**Respuesta:**

```json
{
  "suma": 33012425828.0,
  "conteo": 3242878,
  "promedio": 10179.98,
  "minimo": 15.0,
  "maximo": 226476.0,
  "mediana": 7662.0,
  "desviacion_estandar": 14453.24
}
```

**Ejemplo con filtros:**

```bash
curl "http://127.0.0.1:8000/v1/estadisticas/ventas?GENERO=Femenino&CANAL=POS"
```

### POST - Estadísticas con filtros personalizados

Recibe filtros en el body JSON.

**Ejemplo:**

```bash
curl -X POST http://127.0.0.1:8000/v1/estadisticas/ventas \
  -H "Content-Type: application/json" \
  -d '{
    "consultas": [
      {"consulta": "GENERO", "valor": "Femenino"},
      {"consulta": "EDAD", "valor": "31"},
      {"consulta": "CANAL", "valor": "POS"}
    ]
  }'
```

**Respuesta:**

```json
{
  "suma": 1500.5,
  "conteo": 42,
  "promedio": 35.73,
  "minimo": 10.0,
  "maximo": 100.0,
  "mediana": 30.0,
  "desviacion_estandar": 25.4
}
```

## Filtros Soportados

| Filtro | Tipo | Valores permitidos | Ejemplo |
|--------|------|--------------------|---------|
| `GENERO` | string | `No especificado`, `Masculino`, `Femenino`, `Otro` | `"Femenino"` |
| `EDAD` | entero | Número entero (0-200) | `"31"` |
| `CANAL` | string | `POS`, `WEB`, `APP`, `CCT`, `APR`, `WPR` | `"POS"` |
| `CODIGO_PRODUCTO` | entero | Código SKU del producto | `"201"` |
| `ID_PERSONA` | string | UUID del cliente | `"7c44465b-9e50-3914-..."` |
| `LOCAL` | entero | Número de local | `"371"` |
| `FECHA_DESDE` | ISO-8601 | Fecha inicio del rango | `"2024-01-01T00:00:00"` |
| `FECHA_HASTA` | ISO-8601 | Fecha fin del rango | `"2024-12-31T23:59:59"` |

## Métricas Calculadas

| Métrica | Descripción |
|---------|-------------|
| `suma` | Suma total de los montos aplicados |
| `conteo` | Cantidad de registros |
| `promedio` | Promedio aritmético (suma / conteo) |
| `minimo` | Valor mínimo |
| `maximo` | Valor máximo |
| `mediana` | Valor central (si conteo es par, promedio de los 2 centrales) |
| `desviacion_estandar` | Raíz cuadrada de la varianza |

## Formato de Errores

Todas las respuestas de error siguen este formato:

### 400 Bad Request (Validación Fallida)

```json
{
  "detail": "El valor 'qwerqwer' no es un número entero válido para EDAD",
  "instance": "/v1/estadisticas/ventas",
  "status": 400,
  "title": "Bad Request",
  "type": "https://developer.mozilla.org/es/docs/Web/HTTP/Reference/Status/400",
  "timestamp": "2026-06-30T20:44:49.201437Z",
  "errorCode": "VF",
  "errorLabel": "Validación Fallida",
  "method": "POST"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Error al calcular la desviación estándar",
  "instance": "/v1/estadisticas/ventas",
  "status": 500,
  "title": "Internal Server Error",
  "type": "https://developer.mozilla.org/es/docs/Web/HTTP/Reference/Status/500",
  "timestamp": "2026-06-30T20:44:49.201437Z",
  "errorCode": "IE",
  "errorLabel": "Error Interno",
  "method": "GET"
}
```

## Estructura del Proyecto

```
cruz-morada-3/
├── ventas_completas.csv          # Datos de ventas (CSV ~665 MB)
├── requirements.txt              # Dependencias Python
├── README.md                     # Este archivo
├── datos.json                    # Datos de prueba
├── app/
│   ├── __init__.py
│   ├── main.py                   # Aplicación FastAPI + carga al inicio
│   ├── config.py                 # Configuración centralizada
│   ├── models.py                 # Schemas Pydantic
│   ├── services/
│   │   ├── csv_loader.py         # Carga paralela del CSV
│   │   ├── data_store.py         # Almacenamiento en memoria
│   │   └── stats_calculator.py   # Cálculos estadísticos
│   ├── routers/
│   │   └── ventas.py             # Endpoints GET y POST
│   ├── validators/
│   │   └── filters.py            # Validación de filtros
│   └── errors/
│       └── handlers.py           # Manejo de errores estándar
└── tests/
    ├── test_stats.py             # Tests de estadísticas
    ├── test_endpoints.py         # Tests de endpoints
    └── test_validators.py        # Tests de validaciones
```

## Variables de Entorno (Opcionales)

| Variable | Descripción | Default |
|----------|-------------|---------|
| `CSV_PATH` | Ruta al archivo CSV | `./ventas_completas.csv` |
| `CHUNK_SIZE` | Tamaño de chunk para procesamiento | `100000` |
| `MAX_WORKERS` | Número de workers paralelos | `4` |

## Tests

```bash
# Ejecutar todos los tests
pytest tests/ -v
```

## Tecnologías

- **Python 3.14** - Lenguaje de programación
- **FastAPI** - Framework web
- **Uvicorn** - Servidor ASGI
- **Pandas** - Procesamiento de datos
- **NumPy** - Cálculos numéricos
- **Pydantic** - Validación de schemas
