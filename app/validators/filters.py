"""Validación y aplicación de filtros sobre los datos de ventas.

Valida que los filtros recibidos (GET query params o POST body)
sean correctos y los aplica sobre el DataFrame.
"""

import logging
from datetime import datetime
from typing import Any, Optional

import pandas as pd

from app.config import (
    CANALES_PERMITIDOS,
    CONSULTAS_PERMITIDAS,
    GENERO_MAP_INVERSO,
    GENEROS_PERMITIDOS,
)
from app.errors.handlers import ValidationError
from app.models import ConsultaItem

logger = logging.getLogger(__name__)

def validar_y_transformar_filtro(filtro: ConsultaItem) -> Any:
    """Valida que un filtro sea correcto y retorna su valor casteado.

    Args:
        filtro: ConsultaItem con el campo 'consulta' y 'valor'.

    Returns:
        El valor ya transformado al tipo correcto (int, datetime, str, UUID).

    Raises:
        ValidationError: Si el filtro no es válido.
    """
    consulta = filtro.consulta.strip().upper()
    valor = filtro.valor.strip()

    if consulta not in CONSULTAS_PERMITIDAS:
        raise ValidationError(
            f"El campo de consulta '{filtro.consulta}' no es válido. "
            f"Valores permitidos: {', '.join(CONSULTAS_PERMITIDAS)}"
        )

    if consulta == "GENERO":
        generos_lower = {g.lower(): g for g in GENEROS_PERMITIDOS}
        valor_lower = valor.lower()
        
        if valor_lower not in generos_lower:
            raise ValidationError(
                f"El valor '{valor}' no es válido para GENERO. "
                f"Valores permitidos: {', '.join(GENEROS_PERMITIDOS)}"
            )
        return generos_lower[valor_lower]

    elif consulta == "EDAD":
        try:
            edad = int(valor)
            if edad < 0 or edad > 200:
                raise ValidationError(
                    f"El valor '{valor}' no es una edad válida. "
                    "Debe ser un número entero entre 0 y 200"
                )
            return edad
        except ValueError:
            raise ValidationError(
                f"El valor '{valor}' no es un número entero válido para EDAD"
            )

    elif consulta == "CANAL":
        if valor.upper() not in CANALES_PERMITIDOS:
            raise ValidationError(
                f"El valor '{valor}' no es válido para CANAL. "
                f"Valores permitidos: {', '.join(CANALES_PERMITIDOS)}"
            )
        return valor.upper()

    elif consulta == "CODIGO_PRODUCTO":
        try:
            return int(valor)
        except ValueError:
            raise ValidationError(
                f"El valor '{valor}' no es un número entero válido "
                "para CODIGO_PRODUCTO"
            )

    elif consulta == "ID_PERSONA":
        import uuid
        try:
            uuid_obj = uuid.UUID(valor)
            # Retornamos el string del UUID para mantener compatibilidad con el DataFrame
            return str(uuid_obj)
        except ValueError:
            raise ValidationError(
                f"El valor '{valor}' no es un identificador UUID válido para ID_PERSONA"
            )

    elif consulta == "LOCAL":
        try:
            return int(valor)
        except ValueError:
            raise ValidationError(
                f"El valor '{valor}' no es un número entero válido "
                "para el ID de tienda"
            )

    elif consulta in ("FECHA_DESDE", "FECHA_HASTA"):
        try:
            # Validamos con fromisoformat para ser estrictos con el formato
            # y retornamos pd.to_datetime para consistencia con Pandas
            dt = datetime.fromisoformat(valor)
            return pd.to_datetime(dt)
        except (ValueError, TypeError):
            raise ValidationError(
                f"El valor '{valor}' no es una fecha válida en formato ISO-8601 "
                f"para {consulta}"
            )

    return valor


def validar_consultas(consultas: Optional[list[ConsultaItem]]) -> list[dict[str, Any]]:
    """Valida una lista completa de filtros y los transforma.

    Args:
        consultas: Lista de filtros a validar.

    Returns:
        Lista de diccionarios con las consultas y sus valores ya casteados.

    Raises:
        ValidationError: Si algún filtro no es válido o la lista está vacía/nula.
    """
    if consultas is None or len(consultas) == 0:
        raise ValidationError(
            "El campo 'consultas' no puede estar vacío o nulo"
        )

    filtros_transformados = []
    for filtro in consultas:
        if not filtro.consulta or not filtro.consulta.strip():
            raise ValidationError(
                "El campo 'consulta' no puede estar vacío"
            )
        if filtro.valor is None:
            raise ValidationError(
                f"El campo 'valor' no puede ser nulo para la consulta "
                f"'{filtro.consulta}'"
            )
        
        valor_casteado = validar_y_transformar_filtro(filtro)
        filtros_transformados.append({
            "consulta": filtro.consulta.strip().upper(),
            "valor": valor_casteado
        })
        
    return filtros_transformados


def aplicar_filtros(
    df: pd.DataFrame, consultas_transformadas: list[dict[str, Any]]
) -> pd.DataFrame:
    """Aplica los filtros validados y transformados sobre el DataFrame.

    Args:
        df: DataFrame completo con los datos de ventas.
        consultas_transformadas: Lista de filtros ya parseados a su tipo correcto.

    Returns:
        DataFrame filtrado según los criterios proporcionados.
    """
    if not consultas_transformadas:
        return df

    # Crear una máscara booleana inicial (todos verdaderos)
    mask = pd.Series(True, index=df.index)

    for filtro in consultas_transformadas:
        consulta = filtro["consulta"]
        valor = filtro["valor"]

        if consulta == "GENERO":
            mask &= (df["GENERO"] == valor)

        elif consulta == "EDAD":
            # ya es entero
            mask &= (df["EDAD"] == valor)

        elif consulta == "CANAL":
            mask &= (df["CANAL"] == valor)

        elif consulta == "CODIGO_PRODUCTO":
            # ya es entero
            mask &= (df["CODIGO_PRODUCTO"] == valor)

        elif consulta == "ID_PERSONA":
            mask &= (df["ID_PERSONA"] == valor)

        elif consulta == "LOCAL":
            # ya es entero
            mask &= (df["LOCAL"] == valor)

        elif consulta == "FECHA_DESDE":
            # ya es datetime
            mask &= (df["FECHA"] >= valor)

        elif consulta == "FECHA_HASTA":
            # ya es datetime
            mask &= (df["FECHA"] <= valor)

    df_filtrado = df[mask]

    logger.info(
        "Filtros aplicados: %d filtros, %d filas resultantes",
        len(consultas_transformadas),
        len(df_filtrado),
    )

    return df_filtrado
