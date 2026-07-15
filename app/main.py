import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.errors.handlers import register_error_handlers
from app.routers.ventas import router as ventas_router
from app.services.csv_loader import cargar_csv
from app.services.data_store import data_store

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación.

    Al iniciar, carga el CSV de ventas en memoria usando procesamiento
    paralelo. Los datos quedan disponibles para los endpoints.
    """
    logger.info("Iniciando aplicación Cruz Morada API...")

    # Carga desatendida del CSV al iniciar
    try:
        df = cargar_csv()
        data_store.set_dataframe(df)
        logger.info(
            "Datos cargados exitosamente: %d filas disponibles",
            data_store.row_count,
        )
    except FileNotFoundError:
        logger.error("No se encontró el archivo CSV. Los endpoints no funcionarán.")
    except Exception as e:
        logger.error("Error al cargar el CSV: %s", e)

    yield
    logger.info("Cerrando aplicación Cruz Morada API...")


app = FastAPI(
    title="Cruz Morada - API de Estadísticas de Ventas",
    description=(
        "Servicio REST para obtener un resumen estadístico integral "
        "de los datos de ventas de Cruz Morada.\n\n"
        "## Funcionalidades\n\n"
        "- **GET /v1/estadisticas/ventas**: Estadísticas con filtros via query params\n"
        "- **POST /v1/estadisticas/ventas**: Estadísticas con filtros via body JSON\n\n"
        "## Métricas disponibles\n\n"
        "Suma, conteo, promedio, mínimo, máximo, mediana y desviación estándar "
        "sobre los montos de venta.\n\n"
        "## Filtros soportados\n\n"
        "GENERO, EDAD, CANAL, CODIGO_PRODUCTO, ID_PERSONA, LOCAL, "
        "FECHA_DESDE, FECHA_HASTA"
    ),
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "Cruz Morada - Equipo de Desarrollo",
    },
    license_info={
        "name": "MIT",
    },
)

# Registrar error handlers y router
register_error_handlers(app)
app.include_router(ventas_router)


@app.get("/", tags=["Health"])
async def health_check():
    """Endpoint de salud para verificar que el servidor está activo."""
    return {
        "status": "ok",
        "servicio": "Cruz Morada API v1.0.0",
        "datos_cargados": data_store.is_loaded,
        "total_filas": data_store.row_count,
    }
