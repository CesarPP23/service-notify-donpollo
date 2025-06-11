# notifier/services/gcs_service.py
import os
import logging
from google.cloud import storage
from notifier.config import BUCKET_NAME, ARCHIVOS_REQUERIDOS

def descargar_archivos_de_gcs():
    """
    Descarga todos los archivos necesarios de GCS a la carpeta /tmp del contenedor.
    Devuelve un diccionario con las rutas locales a esos archivos.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    rutas_locales = {}

    logging.info(f"Descargando archivos desde el bucket gs://{BUCKET_NAME}...")

    for nombre_clave, nombre_archivo in ARCHIVOS_REQUERIDOS.items():
        try:
            blob = bucket.blob(nombre_archivo)
            destination_path = os.path.join("/tmp", nombre_archivo)
            blob.download_to_filename(destination_path)
            rutas_locales[nombre_clave] = destination_path
            logging.info(f"-> Archivo '{nombre_archivo}' descargado a '{destination_path}'.")
        except Exception as e:
            logging.error(f"FALLO al descargar '{nombre_archivo}': {e}")
            raise  # Detenemos la ejecución si un archivo esencial no se puede descargar

    return rutas_locales