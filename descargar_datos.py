import logging
import sys

import gdown

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ID del archivo en Google Drive (obtenido del enlace)
FILE_ID = "1UC8S8WwJh6EjYdDyqczj_mXfXxn_kmde"
OUTPUT_FILE = "ventas_completas.csv"

def descargar_csv():
    logger.info("Iniciando descarga del archivo CSV desde Google Drive...")
    try:
        # Usar el parámetro 'id' en lugar de la URL completa suele resolver
        # problemas de permisos y avisos de escaneo de virus con gdown
        output = gdown.download(id=FILE_ID, output=OUTPUT_FILE, quiet=False)
        
        if output:
            logger.info(f"Descarga exitosa. El archivo se guardó como: {output}")
        else:
            logger.error("No se pudo descargar el archivo.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error durante la descarga: {e}")
        sys.exit(1)

if __name__ == "__main__":
    descargar_csv()
