"""Manejo de errores estándar para la API.

Define excepciones personalizadas y handlers que formatean
las respuestas de error según la especificación requerida.
"""

import logging
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Error de validación de datos (400 Bad Request)."""

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(self.detail)


class InternalError(Exception):
    """Error interno del servidor (500 Internal Server Error)."""

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(self.detail)


def _build_error_response(
    detail: str,
    status: int,
    title: str,
    error_code: str,
    error_label: str,
    method: str,
) -> dict:
    """Construye el diccionario de respuesta de error según el formato requerido.

    Args:
        detail: Descripción detallada del error.
        status: Código de estado HTTP.
        title: Título del error HTTP.
        error_code: Código interno del error (VF, IE).
        error_label: Etiqueta del error.
        method: Método HTTP de la solicitud.

    Returns:
        Diccionario con el formato de error estándar.
    """
    status_urls = {
        400: "https://developer.mozilla.org/es/docs/Web/HTTP/Reference/Status/400",
        500: "https://developer.mozilla.org/es/docs/Web/HTTP/Reference/Status/500",
    }

    return {
        "detail": detail,
        "instance": "/v1/estadisticas/ventas",
        "status": status,
        "title": title,
        "type": status_urls.get(status, ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "errorCode": error_code,
        "errorLabel": error_label,
        "method": method,
    }


def register_error_handlers(app: FastAPI) -> None:
    """Registra los handlers de errores en la aplicación FastAPI.

    Args:
        app: Instancia de la aplicación FastAPI.
    """

    @app.exception_handler(ValidationError)
    async def validation_error_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        """Handler para errores de validación (400)."""
        logger.warning("Validación fallida [%s]: %s", request.method, exc.detail)
        body = _build_error_response(
            detail=exc.detail,
            status=400,
            title="Bad Request",
            error_code="VF",
            error_label="Validación Fallida",
            method=request.method,
        )
        return JSONResponse(status_code=400, content=body)

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handler para errores de validación de Pydantic/FastAPI (400).

        Captura errores como JSON malformado o campos faltantes.
        """
        # Extraer un mensaje legible de los errores de Pydantic
        errors = exc.errors()
        if errors:
            first_error = errors[0]
            field = " -> ".join(str(loc) for loc in first_error.get("loc", []))
            msg = first_error.get("msg", "Error de validación")
            detail = f"Error en campo '{field}': {msg}"
        else:
            detail = "Error de validación en la solicitud"

        logger.warning(
            "Validación de request fallida [%s]: %s", request.method, detail
        )
        body = _build_error_response(
            detail=detail,
            status=400,
            title="Bad Request",
            error_code="VF",
            error_label="Validación Fallida",
            method=request.method,
        )
        return JSONResponse(status_code=400, content=body)

    @app.exception_handler(InternalError)
    async def internal_error_handler(
        request: Request, exc: InternalError
    ) -> JSONResponse:
        """Handler para errores internos del servidor (500)."""
        logger.error("Error interno [%s]: %s", request.method, exc.detail)
        body = _build_error_response(
            detail=exc.detail,
            status=500,
            title="Internal Server Error",
            error_code="IE",
            error_label="Error Interno",
            method=request.method,
        )
        return JSONResponse(status_code=500, content=body)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handler para errores HTTP estándar (como 404 Not Found o 405 Method Not Allowed)."""
        logger.warning(
            "Error HTTP %d [%s] en %s: %s",
            exc.status_code,
            request.method,
            request.url.path,
            exc.detail,
        )
        
        status_titles = {
            404: "Not Found",
            405: "Method Not Allowed",
        }
        title = status_titles.get(exc.status_code, "HTTP Error")
        
        body = _build_error_response(
            detail=exc.detail,
            status=exc.status_code,
            title=title,
            error_code="HTTP",
            error_label=title,
            method=request.method,
        )
        return JSONResponse(status_code=exc.status_code, content=body)

    @app.exception_handler(Exception)
    async def general_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handler genérico para excepciones no manejadas (500)."""
        logger.error(
            "Error no manejado [%s]: %s - %s",
            request.method,
            type(exc).__name__,
            str(exc),
        )
        body = _build_error_response(
            detail=f"Error interno del servidor: {type(exc).__name__}",
            status=500,
            title="Internal Server Error",
            error_code="IE",
            error_label="Error Interno",
            method=request.method,
        )
        return JSONResponse(status_code=500, content=body)
