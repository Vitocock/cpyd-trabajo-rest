"""Almacenamiento en memoria del DataFrame de ventas.

Singleton que mantiene el DataFrame procesado en memoria
para acceso rápido desde los endpoints.
"""

import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


class DataStore:
    """Singleton que almacena el DataFrame de ventas en memoria."""

    _instance: Optional["DataStore"] = None
    _df: Optional[pd.DataFrame] = None
    _loaded: bool = False

    def __new__(cls) -> "DataStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set_dataframe(self, df: pd.DataFrame) -> None:
        """Almacena el DataFrame procesado.

        Args:
            df: DataFrame de pandas con los datos de ventas ya procesados.
        """
        self._df = df
        self._loaded = True
        logger.info(
            "DataFrame almacenado: %d filas, %.2f MB en memoria",
            len(df),
            df.memory_usage(deep=True).sum() / (1024 * 1024),
        )

    def get_dataframe(self) -> pd.DataFrame:
        """Retorna el DataFrame almacenado.

        Returns:
            DataFrame con los datos de ventas.

        Raises:
            RuntimeError: Si los datos aún no han sido cargados.
        """
        if not self._loaded or self._df is None:
            raise RuntimeError(
                "Los datos de ventas aún no han sido cargados. "
                "Espere a que la aplicación termine de iniciar."
            )
        return self._df

    @property
    def is_loaded(self) -> bool:
        """Indica si los datos ya fueron cargados."""
        return self._loaded

    @property
    def row_count(self) -> int:
        """Retorna la cantidad de filas cargadas."""
        if self._df is None:
            return 0
        return len(self._df)


# Instancia global del DataStore
data_store = DataStore()
