"""Carga paralela del CSV de ventas.

Utiliza pandas con chunking y concurrent.futures para procesar
el archivo CSV de gran volumen de manera eficiente.
"""

import logging
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import date

import numpy as np
import pandas as pd

from app.config import (
    CHUNK_SIZE,
    CSV_DELIMITER,
    CSV_ENCODING,
    CSV_PATH,
    CSV_QUOTECHAR,
    GENERO_MAP,
    MAX_WORKERS,
)

logger = logging.getLogger(__name__)

# Columnas que necesitamos del CSV y sus tipos
USECOLS = [
    "FECHA",
    "CANAL",
    "SKU",
    "UNIDADES",
    "MONTO APLICADO",
    "LOCAL",
    "CODIGO CLIENTE",
    "FECHA NACIMIENTO",
    "GENERO",
]

# Tipos de datos para optimizar memoria
DTYPES = {
    "CANAL": "category",
    "SKU": "int32",
    "UNIDADES": "int32",
    "MONTO APLICADO": "int64",
    "LOCAL": "int32",
    "CODIGO CLIENTE": "str",
    "GENERO": "str",
}


def _procesar_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    """Limpia y transforma un fragmento (chunk) del CSV.

    Esta función corre en paralelo en distintos núcleos del procesador.
    Se encarga de calcular nuevas columnas y achicar los tipos de datos
    para que el DataFrame final no consuma tanta memoria RAM.

    Específicamente:
    - Calcula la 'EDAD' exacta usando la fecha de la venta y la fecha de nacimiento.
    - Rellena los géneros vacíos con "No especificado".
    - Convierte textos repetitivos a diccionarios internos de Pandas (tipo 'category') para ahorrar memoria.

    Args:
        chunk: El bloque de filas del CSV recién leídas.

    Returns:
        El mismo bloque de filas pero limpio y optimizado.
    """
    # Convertir FECHA a datetime
    chunk["FECHA"] = pd.to_datetime(chunk["FECHA"], format="ISO8601", errors="coerce")

    # Calcular EDAD a partir de FECHA NACIMIENTO relativa a la FECHA de la transacción
    # Se usa cálculo vectorizado para evitar overflow con timedelta en fechas antiguas

    fecha_nac = pd.to_datetime(
        chunk["FECHA NACIMIENTO"], format="%Y-%m-%d", errors="coerce"
    )
    
    edad = chunk["FECHA"].dt.year - fecha_nac.dt.year
    
    # Restar 1 si aún no había cumplido años en la fecha de la venta
    mask_not_birthday_yet = (fecha_nac.dt.month > chunk["FECHA"].dt.month) | (
        (fecha_nac.dt.month == chunk["FECHA"].dt.month) & (fecha_nac.dt.day > chunk["FECHA"].dt.day)
    )
    edad = edad - mask_not_birthday_yet.fillna(False).astype(int)

    # Limpiar y asegurar que sean enteros >= 0, de lo contrario NaN, casteado a Int32
    chunk["EDAD"] = edad.apply(lambda x: int(x) if pd.notna(x) and x >= 0 else np.nan).astype("Int32")

    # Mapear GENERO numérico a texto
    chunk["GENERO"] = (
        chunk["GENERO"].astype(str).map(GENERO_MAP).fillna("No especificado")
    )

    # Renombrar columnas para alinear con los filtros de la API
    chunk = chunk.rename(
        columns={
            "SKU": "CODIGO_PRODUCTO",
            "CODIGO CLIENTE": "ID_PERSONA",
            "MONTO APLICADO": "MONTO_APLICADO",
        }
    )

    # Eliminar columna FECHA NACIMIENTO (ya no se necesita)
    chunk = chunk.drop(columns=["FECHA NACIMIENTO"], errors="ignore")

    # Optimizar tipos de memoria
    chunk["GENERO"] = chunk["GENERO"].astype("category")
    chunk["CANAL"] = chunk["CANAL"].astype("category")

    return chunk


def cargar_csv() -> pd.DataFrame:
    """Carga y procesa el CSV completo usando procesamiento paralelo.

    Lee el archivo en chunks, procesa cada chunk en paralelo usando
    ProcessPoolExecutor, y concatena los resultados.

    Returns:
        DataFrame con todos los datos procesados y listos para consultas.

    Raises:
        FileNotFoundError: Si el archivo CSV no existe.
        Exception: Si ocurre un error durante la carga o procesamiento.
    """
    logger.info("Iniciando carga del CSV: %s", CSV_PATH)
    logger.info(
        "Configuración: chunk_size=%d, max_workers=%d", CHUNK_SIZE, MAX_WORKERS
    )

    inicio = time.time()

    # Leer CSV en chunks
    chunks_reader = pd.read_csv(
        CSV_PATH,
        delimiter=CSV_DELIMITER,
        quotechar=CSV_QUOTECHAR,
        encoding=CSV_ENCODING,
        usecols=USECOLS,
        dtype=DTYPES,
        chunksize=CHUNK_SIZE,
    )

    # Recolectar todos los chunks en una lista
    raw_chunks = list(chunks_reader)
    logger.info("CSV dividido en %d chunks", len(raw_chunks))

    # Procesar chunks en paralelo
    processed_chunks = []
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(_procesar_chunk, chunk) for chunk in raw_chunks]
        for i, future in enumerate(futures):
            resultado = future.result()
            processed_chunks.append(resultado)
            if (i + 1) % 5 == 0 or (i + 1) == len(futures):
                logger.info(
                    "Procesados %d/%d chunks (%.1f%%)",
                    i + 1,
                    len(futures),
                    (i + 1) / len(futures) * 100,
                )

    # Concatenar todos los chunks procesados
    logger.info("Concatenando %d chunks procesados...", len(processed_chunks))
    df = pd.concat(processed_chunks, ignore_index=True)

    duracion = time.time() - inicio
    logger.info(
        "Carga completada: %d filas en %.2f segundos (%.2f MB en memoria)",
        len(df),
        duracion,
        df.memory_usage(deep=True).sum() / (1024 * 1024),
    )

    # Mostrar resumen de los datos cargados
    logger.info("Columnas: %s", list(df.columns))
    logger.info("Tipos:\n%s", df.dtypes.to_string())

    return df
