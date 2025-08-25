# Script para generar reporte de google shetts en dataframes.
from datetime import datetime, date
import pandas as pd
from typing import Union
import logging
# Configurar logging
logger = logging.getLogger(__name__)
def generar_reporte_diario_und_pollos(df_und_google: pd.DataFrame,df_ventas_odo_lastday: pd.DataFrame, fecha_objetivo: Union[str, date, None] = None):
    """
    Genera un reporte diario de unidades de pollo vendidas cruzando stock e información de ventas.
 
    Parámetros:
    ----------
    df_und_google: DataFrame del reporte de stock de google sheet (unidades de pollo)
    
    df_ventas_odoo: DataFrame de ventas de Odoo por producto del último día

    fecha_objetivo : str, datetime.date o None (opcional)
        Fecha que se desea analizar. Si no se proporciona, se usará la última fecha disponible en los datos de ventas.

    Retorna:
    -------
    tuple:
        - df_2_merged : pd.DataFrame
            DataFrame con resumen de stock, ingresos, ventas y última hora de compra por producto.
        - comentario_und_pollos : str
            Comentario resumen con el total de unidades vendidas ese día.
    """
    # Leer los datos
    df_2 = df_und_google
    df_ventas_producto = df_ventas_odo_lastday

    # Filtrar por la fecha objetivo
    df_2 = df_2[df_2['Fecha'] == fecha_objetivo]
    # Hacer merge por producto y fecha
    df_2_merged = df_2.merge(
        df_ventas_producto[['ProductoNombre', 'AsientoCreadoEl_Hora']],
        left_on=['Producto'],
        right_on=['ProductoNombre'],
        how='left'
    )

    # Seleccionar columnas relevantes
    df_2_merged = df_2_merged[['Producto', 'Stock Inicial', 'Ingresos', 'Ventas', 'Stock Final', 'AsientoCreadoEl_Hora']]
    df_2_merged = df_2_merged.rename(columns={'AsientoCreadoEl_Hora': 'Última Compra (hh:mm)'})

    # Seleccionar última hora por producto
    df_2_merged = df_2_merged.sort_values(by=['Producto', 'Última Compra (hh:mm)'], ascending=True)
    df_2_merged = df_2_merged.drop_duplicates(subset=['Producto'], keep='last')

    # Sumar ventas
    und_vendidas_pollos = df_2_merged["Ventas"].sum()

    # Comentario resumen
    comentario_und_pollos = f"{und_vendidas_pollos:,.0f} UND"

    return df_2_merged, comentario_und_pollos