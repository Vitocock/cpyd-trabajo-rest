"""Cálculo de estadísticas sobre los datos de ventas.

Implementa las fórmulas requeridas: suma, conteo, promedio,
mínimo, máximo, mediana y desviación estándar.
"""

import logging

import numpy as np
import pandas as pd

from app.models import EstadisticasResponse

logger = logging.getLogger(__name__)


def calcular_estadisticas(df: pd.DataFrame) -> EstadisticasResponse:
    """Calcula el resumen estadístico sobre la columna MONTO_APLICADO.
    
    Toma las filas de ventas (ya sean todas o solo las filtradas) y
    calcula métricas como suma, promedio, y desviación estándar.
    
    Nota: La desviación estándar se calcula usando la fórmula poblacional (ddof=0).

    Args:
        df: DataFrame filtrado (o completo) con los datos de ventas.

    Returns:
        EstadisticasResponse con todas las métricas calculadas.

    Raises:
        ValueError: Si el DataFrame está vacío o no tiene la columna requerida.
        RuntimeError: Si ocurre un error durante el cálculo.
    """
    if df.empty:
        return EstadisticasResponse(
            suma=0.0, conteo=0, promedio=0.0, minimo=0.0, maximo=0.0, mediana=0.0, desviacion_estandar=0.0
        )

    if "MONTO_APLICADO" not in df.columns:
        raise RuntimeError("La columna 'MONTO_APLICADO' no existe en los datos")

    montos = df["MONTO_APLICADO"].dropna()

    if montos.empty:
        return EstadisticasResponse(
            suma=0.0, conteo=0, promedio=0.0, minimo=0.0, maximo=0.0, mediana=0.0, desviacion_estandar=0.0
        )

    try:
        conteo = int(len(montos))
        suma = float(montos.sum())
        promedio = suma / conteo
        minimo = float(montos.min())
        maximo = float(montos.max())

        # Mediana: valor central. Si conteo es par, promedio de los 2 centrales
        mediana = float(np.median(montos.values))

        # Desviación estándar: raíz cuadrada de la varianza (poblacional)
        desviacion_estandar = float(np.std(montos.values, ddof=0))

        return EstadisticasResponse(
            suma=suma,
            conteo=conteo,
            promedio=promedio,
            minimo=minimo,
            maximo=maximo,
            mediana=mediana,
            desviacion_estandar=desviacion_estandar,
        )

    except Exception as e:
        logger.error("Error al calcular estadísticas: %s", e)
        raise RuntimeError(f"Error al calcular estadísticas: {e}") from e
