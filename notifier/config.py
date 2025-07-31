# notifier/config.py

# --- Configuración Estática del Proyecto ---
PROJECT_ID = ""
BUCKET_NAME = "bucket-donpollo-reportes-micasero" #nombre del bucket de Google Cloud Storage (GCS) donde estarán los archivos excel
SENDER_EMAIL_SECRET_ID = "SENDER_EMAIL"  # El ID del secreto para el email remitente
#SENDGRID_API_KEY_SECRET_ID = "SENDGRID_API_KEY" # El ID del secreto para la clave de SendGrid
GET_GMAIL_CREDENTIALS_SECRET_ID = "gmail-oauth-credentials"  # El ID del secreto para las credenciales de Gmail OAuth2
# Lista de archivos que el bot necesita para trabajar
# Estos son los nombres de los archivos como están en el bucket de GCS
ARCHIVOS_REQUERIDOS = {
    "ventas": "Comprobantes mi casero.xlsx",
    "nc": "NC mi casero.xlsx",
    "presupuesto": "Consolidado.xlsx",
    # "key_gspread": "key_mi_casero.json" # La llave para Google Sheets
}

# --- Configuración para el Correo ---
RECIPIENTS = ["klkl@klkl.pe"]
POWER_BI_LINK = ""

# --- Constantes para la lógica de reportes ---
MESES_DICT = {
    "Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Ago": 8, "Set": 9, "Oct": 10, "Nov": 11, "Dic": 12
}

ACCESOS_GSPREAD = {
    'form_mov_pollos': {
        'SHEET_ID': '',
        'GID': ''
    }
}
