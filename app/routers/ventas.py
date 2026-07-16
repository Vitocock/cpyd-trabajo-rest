"""Endpoints de estadísticas de ventas.

Implementa las operaciones GET y POST en /v1/estadisticas/ventas
para consultar el resumen estadístico con filtros opcionales.
"""

import logging
from datetime import date
from typing import Optional

from fastapi import APIRouter, Query

from app.errors.handlers import InternalError, ValidationError
from app.models import ConsultaItem, ConsultaRequest, EstadisticasResponse
from app.services.data_store import data_store
from app.services.stats_calculator import calcular_estadisticas
from app.validators.filters import aplicar_filtros, validar_consultas

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/v1/estadisticas",
    tags=["Estadísticas de Ventas"],
)


@router.get(
    "/ventas",
    response_model=EstadisticasResponse,
    summary="Consultar estadísticas de ventas",
    description=(
        "Devuelve estadísticas de ventas con filtros opcionales "
        "mediante query params. Sin filtros retorna estadísticas globales."
    ),
    responses={
        400: {"description": "Validación fallida"},
        500: {"description": "Error interno del servidor"},
    },
)
async def get_estadisticas(
    GENERO: Optional[str] = Query(
        None,
        description="Filtrar por género: No especificado, Masculino, Femenino, Otro",
    ),
    EDAD: Optional[int] = Query(
        None,
        description="Filtrar por edad (número entero)",
    ),
    CANAL: Optional[str] = Query(
        None,
        description="Filtrar por canal: POS, WEB, APP, CCT, APR, WPR",
    ),
    CODIGO_PRODUCTO: Optional[int] = Query(
        None,
        description="Filtrar por código de producto (SKU)",
    ),
    ID_PERSONA: Optional[str] = Query(
        None,
        description="Filtrar por ID de persona (UUID del cliente)",
    ),
    LOCAL: Optional[int] = Query(
        None,
        description="Filtrar por número de local",
    ),
    FECHA_DESDE: Optional[date] = Query(
        None,
        description="Fecha desde (ej: 2024-01-01)",
    ),
    FECHA_HASTA: Optional[date] = Query(
        None,
        description="Fecha hasta (ej: 2024-12-31)",
    ),
) -> EstadisticasResponse:
    """GET /v1/estadisticas/ventas — Estadísticas con filtros via query params."""
    try:
        df = data_store.get_dataframe()

        # Construir lista de filtros a partir de los query params proporcionados
        consultas = []
        params = {
            "GENERO": GENERO,
            "EDAD": EDAD,
            "CANAL": CANAL,
            "CODIGO_PRODUCTO": CODIGO_PRODUCTO,
            "ID_PERSONA": ID_PERSONA,
            "LOCAL": LOCAL,
            "FECHA_DESDE": FECHA_DESDE,
            "FECHA_HASTA": FECHA_HASTA,
        }

        for nombre, valor in params.items():
            if valor is not None:
                consultas.append(ConsultaItem(consulta=nombre, valor=str(valor)))

        # Si hay filtros, validar y aplicar
        if consultas:
            consultas_transformadas = validar_consultas(consultas)
            df = aplicar_filtros(df, consultas_transformadas)

        return calcular_estadisticas(df)

    except ValidationError as e:
        raise ValidationError(str(e)) from e
    except RuntimeError as e:
        raise InternalError(str(e)) from e


@router.post(
    "/ventas",
    response_model=EstadisticasResponse,
    summary="Consultar estadísticas con filtros personalizados",
    description=(
        "Devuelve estadísticas de ventas con filtros personalizados "
        "enviados en el body JSON. Los filtros son opcionales y se pueden "
        "combinar libremente."
    ),
    responses={
        400: {"description": "Validación fallida"},
        500: {"description": "Error interno del servidor"},
    },
)
async def post_estadisticas(
    body: ConsultaRequest,
) -> EstadisticasResponse:
    """POST /v1/estadisticas/ventas — Estadísticas con filtros via body JSON."""
    try:
        df = data_store.get_dataframe()

        # Validar los filtros del body y transformarlos
        consultas_transformadas = validar_consultas(body.consultas)

        # Aplicar filtros
        df = aplicar_filtros(df, consultas_transformadas)

        return calcular_estadisticas(df)

    except ValidationError as e:
        raise ValidationError(str(e)) from e
    except RuntimeError as e:
        raise InternalError(str(e)) from e
