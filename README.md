# Cruz Morada - API de Estadísticas de Ventas

# Integrantes
- Víctor Morales
- Julián Vidal
- Matías Ziade 

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

Se recomienda el uso de un entorno virtual para evitar conflictos con paquetes del sistema (especialmente en distribuciones modernas de Linux).

1. Clona el repositorio:
   ```bash
   git clone <https://github.com/Vitocock/cpyd-trabajo-rest.git>
   cd cpyd-trabajo-rest
   ```

2. Crea un entorno virtual e instala las dependencias:
   ```bash
   python -m venv venv
   # En Windows: venv\Scripts\activate
   # En Linux/Mac: source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Inicia la aplicación con un solo comando:**
   El proyecto incluye un script de arranque unificado (`run.py`). Este script funciona de manera completamente desatendida: verifica si tienes el CSV gigante descargado, si no lo tienes lo descarga automáticamente desde Google Drive, e inmediatamente después levanta el servidor de la API, el cual procesará y cargará los datos en RAM.
   
   ```bash
   python run.py
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
  "suma": 20649356290.0,
  "conteo": 2086258,
  "promedio": 9897.8,
  "minimo": 15.0,
  "maximo": 226475.0,
  "mediana": 7476.0,
  "desviacion_estandar": 14565.87
}
```

## Filtros Soportados

| Filtro | Tipo | Valores permitidos | Ejemplo |
|--------|------|--------------------|---------|
| `GENERO` | string | `Masculino`, `Femenino`, `No especificado`, `Otro` | `"Femenino"` |
| `EDAD` | entero | Número entero (0-200) | `"31"` |
| `CANAL` | string | `POS`, `WEB`, `APP`, `CCT`, `APR`, `WPR` | `"POS"` |
| `CODIGO_PRODUCTO` | entero | Código SKU del producto | `"201"` |
| `ID_PERSONA` | string | UUID del cliente | `"7c44465b-9e50-3914-..."` |
| `LOCAL` | entero | Número de local | `"371"` |
| `FECHA_DESDE` | fecha | Fecha inicio del rango (YYYY-MM-DD) | `"2024-01-01"` |
| `FECHA_HASTA` | fecha | Fecha fin del rango (YYYY-MM-DD) | `"2024-12-31"` |

> **Nota sobre GENERO:** El dataset actual contiene únicamente registros con valores `Masculino` y `Femenino`. Los filtros `No especificado` y `Otro` son aceptados por la API (según la especificación), pero retornarán `conteo: 0` dado que no existen registros con dichos valores en los datos de origen.

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
cpyd-trabajo-rest/
├── ventas_completas.csv          # Datos de ventas (CSV ~665 MB)
├── descargar_datos.py            # Script módulo de descarga desde GDrive
├── run.py                        # Script de arranque unificado (descarga + API)
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



## Tests

Para ejecutar la batería completa de pruebas unitarias y de integración (asegúrate de estar en el entorno virtual):

```bash
# Ejecutar todos los tests
python -m pytest tests/ -v
```

## Tecnologías

- **Python 3.14** - Lenguaje de programación
- **FastAPI** - Framework web
- **Uvicorn** - Servidor ASGI
- **Pandas** - Procesamiento de datos
- **NumPy** - Cálculos numéricos
- **Pydantic** - Validación de schemas

## Justificación de Decisiones de Preprocesamiento

El script de carga de datos (`app/services/csv_loader.py`) realiza las siguientes transformaciones para optimizar el rendimiento y asegurar que los datos estén limpios antes de recibrir consultas:

1. **Cálculo de Variables:** La columna `EDAD` se calcula usando la `FECHA NACIMIENTO` y la fecha de la transacción. Después de calcularla, la columna de fecha de nacimiento original se elimina de la tabla para liberar espacio en la memoria RAM.
2. **Tratamiento de Nulos:** Los valores vacíos en la columna `GENERO` se reemplazan por el texto `"No especificado"` para no perder esas ventas en las estadísticas totales. Si al calcular la edad da un valor negativo o inválido, se deja como nulo usando el tipo de dato `Int32` de Pandas (que soporta nulos sin colapsar).
3. **Optimización de Memoria (Downcasting):** Se asignan tipos de datos más eficientes. Las columnas de texto que repiten pocos valores (`CANAL`, `GENERO`) se convierten al tipo `category` de Pandas (que funciona como un diccionario numérico interno). Los campos numéricos se achican a `int32` e `int64`. Gracias a esto, el archivo CSV de ~665 MB termina ocupando solo ~528 MB en la memoria.

## Escalabilidad y Bajo Consumo de Recursos

Para poder cargar los ~ 3.2 millones de registros (~665 MB) rápido y sin que se trabe el servidor, el sistema utiliza dos estrategias principales:

**1. Procesamiento Paralelo (Escalabilidad de CPU):**
Debido a la restricción del GIL (Global Interpreter Lock) de Python, un enfoque secuencial utilizaría únicamente un núcleo del procesador. El servicio sortea esta limitación mediante el uso de `concurrent.futures.ProcessPoolExecutor`. Este mecanismo genera procesos paralelos independientes que distribuyen la carga computacional de transformación de datos (parseo de fechas, cálculo de edades y mapeos categóricos) a través de los múltiples núcleos disponibles de la CPU (`MAX_WORKERS=4`). Esto garantiza que el sistema escale de forma concurrente ante incrementos masivos en el volumen de datos.

**2. Técnica de Chunking y Downcasting:**
En lugar de intentar cargar todo el archivo de golpe a la memoria (lo que causaría un error de falta de RAM), el CSV se lee a trozos (chunks) en bloques de 100.000 filas usando el parámetro `chunksize`. A medida que se lee cada bloque, se aplican las reducciones de tipos de datos mencionadas anteriormente. 

**Benchmark Base de Referencia:**
- **Tiempo de carga asíncrona:** ~7.7 a 8.5 segundos.
- **Hardware de pruebas:** AMD Ryzen 5 8400F, 16 GB de RAM DDR5 5600 MT/s, Almacenamiento SSD M.2 NVMe.
- **Diseño Desatendido:** El sistema funciona completamente en segundo plano y carga el CSV de manera automática al arrancar el framework, sin necesidad de que un operador interactúe con la consola.

## Detalles de las Estadísticas

El archivo `stats_calculator.py` es el encargado de procesar los datos una vez que se aplican los filtros ingresados por el usuario.

**Notas sobre el Cálculo:**
- Los resultados (suma, promedio, mediana, etc.) se calculan exclusivamente sobre los datos que coincidan con los filtros de búsqueda y no representan a la tabla completa a menos que se haga una consulta sin filtros.
- Para el cálculo de la **desviación estándar** se utiliza la fórmula poblacional de numpy (`ddof=0`), asumiendo que los datos resultantes del filtro representan el total de la partición de interés y no una muestra.
