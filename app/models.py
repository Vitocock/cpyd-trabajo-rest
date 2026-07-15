from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# Respuesta exitosa
# ──────────────────────────────────────────────
class EstadisticasResponse(BaseModel):
    """Respuesta con el resumen estadístico de ventas."""

    suma: float = Field(..., description="Suma total de los montos aplicados")
    conteo: int = Field(..., description="Cantidad de registros")
    promedio: float = Field(..., description="Promedio (suma / conteo)")
    minimo: float = Field(..., description="Valor mínimo")
    maximo: float = Field(..., description="Valor máximo")
    mediana: float = Field(..., description="Valor central de los datos")
    desviacion_estandar: float = Field(
        ..., description="Desviación estándar de los datos"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "suma": 1500.5,
                    "conteo": 42,
                    "promedio": 35.73,
                    "minimo": 10.0,
                    "maximo": 100.0,
                    "mediana": 30.0,
                    "desviacion_estandar": 25.4,
                }
            ]
        }
    }


# ──────────────────────────────────────────────
# Solicitud POST
# ──────────────────────────────────────────────
class ConsultaItem(BaseModel):
    """Un filtro individual con su campo y valor."""

    consulta: str = Field(
        ...,
        description=(
            "Campo por el cual filtrar. Valores permitidos: "
            "GENERO, EDAD, CANAL, CODIGO_PRODUCTO, ID_PERSONA, "
            "LOCAL, FECHA_DESDE, FECHA_HASTA"
        ),
    )
    valor: str = Field(..., description="Valor del filtro")


class ConsultaRequest(BaseModel):
    """Body de la solicitud POST con filtros dinámicos."""

    consultas: list[ConsultaItem] = Field(
        ...,
        description="Lista de filtros a aplicar sobre los datos de ventas",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "consultas": [
                        {"consulta": "GENERO", "valor": "Femenino"},
                        {"consulta": "EDAD", "valor": "31"},
                        {"consulta": "CANAL", "valor": "POS"},
                    ]
                }
            ]
        }
    }


# ──────────────────────────────────────────────
# Respuesta de error estándar
# ──────────────────────────────────────────────
class ErrorResponse(BaseModel):
    """Formato estándar de error según la especificación."""

    detail: str = Field(..., description="Descripción detallada del error")
    instance: str = Field(
        default="/v1/estadisticas/ventas",
        description="Ruta del recurso donde ocurrió el error",
    )
    status: int = Field(..., description="Código de estado HTTP")
    title: str = Field(..., description="Título del error HTTP")
    type: str = Field(..., description="URL de referencia del código de estado")
    timestamp: str = Field(
        ..., description="Marca de tiempo del error en formato ISO-8601"
    )
    errorCode: str = Field(..., description="Código interno del error")
    errorLabel: str = Field(..., description="Etiqueta del error")
    method: str = Field(..., description="Método HTTP de la solicitud")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "detail": "El valor 'X' no es válido para Y",
                    "instance": "/v1/estadisticas/ventas",
                    "status": 400,
                    "title": "Bad Request",
                    "type": "https://developer.mozilla.org/es/docs/Web/HTTP/Reference/Status/400",
                    "timestamp": "2026-06-30T20:44:49.201437123Z",
                    "errorCode": "VF",
                    "errorLabel": "Validación Fallida",
                    "method": "POST",
                }
            ]
        }
    }
