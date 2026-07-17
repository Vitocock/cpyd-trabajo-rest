"""Tests para el módulo de cálculo de estadísticas."""

import numpy as np
import pandas as pd
import pytest

from app.services.stats_calculator import calcular_estadisticas


class TestCalcularEstadisticas:
    """Tests unitarios para la función calcular_estadisticas."""

    def test_estadisticas_basicas(self):
        """Verifica el cálculo correcto con un DataFrame simple de 3 filas."""
        df = pd.DataFrame({"MONTO_APLICADO": [1000, 2000, 3000]})
        resultado = calcular_estadisticas(df)

        assert resultado.suma == 6000.0
        assert resultado.conteo == 3
        assert resultado.promedio == 2000.0
        assert resultado.minimo == 1000.0
        assert resultado.maximo == 3000.0
        assert resultado.mediana == 2000.0

    def test_desviacion_estandar_poblacional(self):
        """Verifica que la desviación estándar se calcula como poblacional (ddof=0).

        Se usa un conjunto de datos conocido donde la desviación estándar
        poblacional difiere de la muestral para validar el parámetro ddof=0.
        """
        valores = [10, 20, 30, 40, 50]
        df = pd.DataFrame({"MONTO_APLICADO": valores})
        resultado = calcular_estadisticas(df)

        # Desviación estándar poblacional esperada (ddof=0)
        esperada = float(np.std(valores, ddof=0))
        assert resultado.desviacion_estandar == esperada
    def test_mediana_conteo_par(self):
        """Verifica la mediana cuando el conteo de filas es par.

        Con un número par de elementos, la mediana debe ser el promedio
        de los dos valores centrales.
        """
        df = pd.DataFrame({"MONTO_APLICADO": [10, 20, 30, 40]})
        resultado = calcular_estadisticas(df)

        # Mediana de [10, 20, 30, 40] = (20 + 30) / 2 = 25.0
        assert resultado.mediana == 25.0

    def test_mediana_conteo_impar(self):
        """Verifica la mediana cuando el conteo de filas es impar."""
        df = pd.DataFrame({"MONTO_APLICADO": [10, 20, 30]})
        resultado = calcular_estadisticas(df)

        assert resultado.mediana == 20.0

    def test_dataframe_vacio(self):
        """Verifica que un DataFrame vacío retorna todas las métricas en cero."""
        df = pd.DataFrame({"MONTO_APLICADO": []})
        resultado = calcular_estadisticas(df)

        assert resultado.suma == 0.0
        assert resultado.conteo == 0
        assert resultado.promedio == 0.0
        assert resultado.desviacion_estandar == 0.0

    def test_una_sola_fila(self):
        """Verifica el caso extremo de una sola fila.

        Con un solo valor, la desviación estándar poblacional debe ser 0.0
        y la mediana debe ser igual al valor.
        """
        df = pd.DataFrame({"MONTO_APLICADO": [5000]})
        resultado = calcular_estadisticas(df)

        assert resultado.suma == 5000.0
        assert resultado.conteo == 1
        assert resultado.promedio == 5000.0
        assert resultado.minimo == 5000.0
        assert resultado.maximo == 5000.0
        assert resultado.mediana == 5000.0
        assert resultado.desviacion_estandar == 0.0

    def test_columna_inexistente_lanza_error(self):
        """Verifica que se lanza RuntimeError si no existe MONTO_APLICADO."""
        df = pd.DataFrame({"OTRA_COLUMNA": [100, 200]})

        with pytest.raises(RuntimeError, match="MONTO_APLICADO"):
            calcular_estadisticas(df)

    def test_valores_con_nulos(self):
        """Verifica que los valores NaN se excluyen correctamente del cálculo."""
        df = pd.DataFrame({"MONTO_APLICADO": [100, np.nan, 300, np.nan, 500]})
        resultado = calcular_estadisticas(df)

        # Solo 3 valores válidos: 100, 300, 500
        assert resultado.conteo == 3
        assert resultado.suma == 900.0
        assert resultado.promedio == 300.0

