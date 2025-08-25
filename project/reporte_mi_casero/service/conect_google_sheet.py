from google.oauth2.service_account import Credentials
import pandas as pd
import logging
import gspread
from gspread.exceptions import SpreadsheetNotFound

# Configurar logging
logger = logging.getLogger(__name__)

def get_excel_stock_und(form: str, GOOGLE_SHEET_CREDENTIALS: str, ACCESOS_SHEET_GOOGLE: dict) -> pd.DataFrame:
    """
    Obtiene los datos del formulario de Google Sheets de forma segura,
    manejando errores de conexión, autenticación y datos.
    """
    logger.info(f"▶️ Iniciando la obtención de datos para el formulario: '{form}'")

    # Verificar si el formulario está configurado antes de intentar la conexión
    if form not in ACCESOS_SHEET_GOOGLE:
        logger.error(f"❌ Configuración no encontrada para el formulario '{form}'.")
        return pd.DataFrame()

    SHEET_ID = ACCESOS_SHEET_GOOGLE[form].get("SHEET_ID")
    if not SHEET_ID:
        logger.error(f"❌ No se encontró 'SHEET_ID' en la configuración para el formulario '{form}'.")
        return pd.DataFrame()

    try:
        # --- Bloque Crítico: Interacción con la API de Google ---
        logger.info("🔐 Autenticando con la API de Google Sheets...")
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(GOOGLE_SHEET_CREDENTIALS, scopes=scopes)
        client = gspread.authorize(creds)

        logger.info(f"📄 Abriendo la hoja de cálculo con ID: {SHEET_ID}")
        spreadsheet = client.open_by_key(SHEET_ID)
        
        worksheet = spreadsheet.sheet1
        logger.info(f"✅ Hoja de cálculo '{worksheet.title}' abierta correctamente.")

        data_formulario = worksheet.get_all_values()

        # --- Validación de Datos Obtenidos ---
        if not data_formulario or len(data_formulario) < 2:
            logger.warning(f"⚠️ La hoja de cálculo '{worksheet.title}' está vacía o solo contiene encabezados.")
            return pd.DataFrame()

        headers = data_formulario[0]
        df_mov_pollos = pd.DataFrame(data_formulario[1:], columns=headers)

        logger.info(f"✅ Datos obtenidos y convertidos a DataFrame exitosamente. Filas: {len(df_mov_pollos)}")
        return df_mov_pollos

    # --- Manejo de Errores Específicos ---
    except FileNotFoundError:
        logger.error(f"❌ Error Crítico: No se encontró el archivo de credenciales en la ruta: '{GOOGLE_SHEET_CREDENTIALS}'")
        return pd.DataFrame()
    except SpreadsheetNotFound:
        logger.error(f"❌ Error Crítico: No se pudo encontrar la hoja de cálculo con ID '{SHEET_ID}'. Verifica el ID y los permisos de la cuenta de servicio.")
        return pd.DataFrame()
    except Exception as e:
        # Captura cualquier otro error inesperado (problemas de red, permisos, etc.)
        logger.error(f"❌ Ocurrió un error inesperado al procesar el formulario '{form}': {e}", exc_info=True)
        return pd.DataFrame()