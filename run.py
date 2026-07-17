import logging
import os

import uvicorn
from descargar_datos import descargar_csv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

CSV_FILE = "ventas_completas.csv"

def main():
    """Script de arranque unificado y desatendido."""
    logger.info("Iniciando script de arranque desatendido de Cruz Morada API...")
    
    # 1. Verificar y descargar CSV si es necesario
    if not os.path.exists(CSV_FILE):
        logger.info("El archivo '%s' no existe localmente. Iniciando descarga...", CSV_FILE)
        descargar_csv()
    else:
        logger.info("El archivo '%s' ya existe localmente. Omitiendo descarga.", CSV_FILE)

    # 2. Iniciar la API (la API cargará el CSV automáticamente en memoria durante el arranque)
    logger.info("Iniciando el servidor de la API REST...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()
