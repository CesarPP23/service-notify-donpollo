import logging
# Configurar logging
logger = logging.getLogger(__name__)
# CONFIGURACIÓN DE BASE DE DATOS SQL SERVER
DB_CONFIG = {
    'driver': '',  # o 'SQL Server' si no tienes el 17
    'server': '',  # Ejemplo: 'localhost' o 'servidor.empresa.com'
    'database': '',  # Nombre de tu base de datos
    'username': '',  # Tu usuario de SQL Server
    'password': '',  # Tu contraseña
    'tabla_ventas': ''  # Nombre de la tabla
}

# RUTA DE ACCESOS AL EXCEL COMPARTIDO.
ACCESOS_SHEET_GOOGLE = {
    'form_mov_pollos': {
        'SHEET_ID': '',
        'GID': ''
    },
    'form_rotura_stock': {
        'SHEET_ID': '',
        'GID': ''
    }
}


# RUTA DE LAS CREDENCIALES PARA GOOGLE SHEETS
GOOGLE_SHEET_CREDENTIALS = "./config/credentials.json"

# Configuración centralizada con metadatos
REPORTES_CONFIG = {
    'ventas_semanal_vs_ppto': {
        'sp': '[dl_bi].[pro_ventaOdoo_get_xArticulo_xSemana_vs_Proyeccion]11',
        'params': [],
        'description': 'Ventas semanales vs presupuesto'
    },
    'ventas_x_sku': {
        'sp': '[dl_bi].pro_ventaOdoo_get_delDia_xCategoriaDetalle',
        'params': ['fecha'],
        'description': 'Ventas por SKU del día'
    },
    'ventas_x_categoria': {
        'sp': '[dl_bi].pro_ventaOdoo_get_delDia_xCategoria', 
        'params': ['fecha'],
        'description': 'Ventas por categoría del día'
    },
    'ventas_comparativo_x_semana_x_dia': {
        'sp': '[dl_bi].pro_ventaOdoo_get_xSemana_xDia',
        'params': ['fecha'],
        'description': 'Comparativo ventas semana vs día'
    }
}


# CONFIGURACIÓN DEL CORREO
DESTINATARIOS = ['cesarestefanop@gmail.com']

SENDER_EMAIL = ''
SMTP_SERVER = 'smtp.office365.com'
SMTP_PORT = 587
PASSWORD = ''