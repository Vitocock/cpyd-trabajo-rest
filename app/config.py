import os
from pathlib import Path


# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración del CSV
CSV_PATH = os.getenv("CSV_PATH", str(BASE_DIR / "ventas_completas.csv"))
CSV_DELIMITER = ";"
CSV_QUOTECHAR = '"'
CSV_ENCODING = "latin-1"

# Procesamiento paralelo
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "100000"))
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))

# Mapeo de género: valor numérico del CSV -> valor textual de la API
GENERO_MAP = {
    "1": "Masculino",
    "2": "Femenino",
}

# Mapeo inverso: valor textual de la API -> valor numérico del CSV
GENERO_MAP_INVERSO = {v: k for k, v in GENERO_MAP.items()}
GENERO_MAP_INVERSO["No especificado"] = "0"
GENERO_MAP_INVERSO["Otro"] = "3"

# Valores permitidos para filtros
GENEROS_PERMITIDOS = ["No especificado", "Masculino", "Femenino", "Otro"]
CANALES_PERMITIDOS = ["POS", "WEB", "APP", "CCT", "APR", "WPR"]
CONSULTAS_PERMITIDAS = [
    "GENERO", "EDAD", "CANAL", "CODIGO_PRODUCTO",
    "ID_PERSONA", "LOCAL", "FECHA_DESDE", "FECHA_HASTA",
]
