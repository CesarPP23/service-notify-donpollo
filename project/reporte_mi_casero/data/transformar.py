# Script para realizar transofrmaciones de datos en el reporte Mi Casero

import pandas as pd
from typing import Union, List, Any
from datetime import datetime, date
import logging
# Configurar logging
logger = logging.getLogger(__name__)

# --- Función para formatear los datos del SQL ---
def format_table(df):
    """ Formate los dataframes cambiando el nombre de las columnas y el tipo de datos """
    columns_nuevas = {
        "Categoria": "Categoría",
        "PrecioPonderado": "Precio Prom",
        "VentaSoles": "Ventas Totales (S/)",
        "Cantidad": "Cantidad Total (kg)",
        "TicketProm": "Ticket Promedio",
        "AsientoCreadoEl_Hora":"Última Compra (hh:mm)",
        "partic":"Participación (%)"}
    #remplazar las columnas al dataframe en caso de que existan
    df.rename(columns=columns_nuevas, inplace=True)
    # ordenar el dataframe de mayor a menor en la columna Participación (%)
    df = df.sort_values(by="Participación (%)", ascending=False)
    #log de las columnas que se han cambiado y las que no
    for col in columns_nuevas.values():
        if col not in df.columns:
            logging.warning(f"La columna '{col}' no se encontró en el DataFrame.")
        else:
            logging.info(f"La columna '{col}' se ha renombrado correctamente.")
    try:
        # Formatear las columnas
        # - Para la columna PrecioPonderado convertirlo a un formato "S/ 0.00"
        df["Precio Prom"] = df["Precio Prom"].apply(lambda x: f"S/ {x:.2f}" if pd.notnull(x) else "-")
        # - Para la columna Ventas Totales convertirlo a un formato separador de miles , y entero
        df["Ventas Totales (S/)"] = df["Ventas Totales (S/)"].apply(lambda x: f"S/ {int(x):,}" if pd.notnull(x) else "-")
        # - Para la columnas cantidad total convertirlo a un formato entero con separador de miles
        df["Cantidad Total (kg)"] = df["Cantidad Total (kg)"].apply(lambda x: f"{int(x):,}" if pd.notnull(x) else "-")
        # - Para la columna Participación
        df["Participación (%)"] =  df["Participación (%)"].apply(lambda x: f"{int(x)}%" if pd.notnull(x) else "-")
        # - Para "Ticket Promedio"
        df["Ticket Promedio"] =  df["Ticket Promedio"].apply(lambda x: f"S/ {int(x):,}" if pd.notnull(x) else "-")
    except KeyError as e:
        logging.error(f"Error al formatear las columnas: {e}")
        return df
    return df

# --- Función para transformar los datos de google sheet ---

def transformar_df_sheet_google(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma un DataFrame de Google Sheets para calcular el stock diario por producto,
    integrando un sistema de logging para trazabilidad y depuración.
    """
    logger.info(f"Iniciando la transformación del DataFrame. Filas iniciales: {len(df)}")

    # --- 1. Limpieza y conversión de tipos ---
    logger.info("Convirtiendo la columna 'Fecha' a formato datetime.")
    # Guardamos el número de filas con fechas nulas ANTES de la conversión
    fechas_nulas_antes = df['Fecha'].isnull().sum()
    df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')

    # Verificamos si la conversión generó nuevos valores nulos (NaT)
    fechas_nulas_despues = df['Fecha'].isnull().sum()
    if fechas_nulas_despues > fechas_nulas_antes:
        filas_con_error = fechas_nulas_despues - fechas_nulas_antes
        logger.warning(f"{filas_con_error} fila(s) contenían un formato de fecha inválido y fueron marcadas como NaT.")
        # Opcional: eliminar filas con fechas inválidas para evitar errores posteriores
        df.dropna(subset=['Fecha'], inplace=True)
        logger.info(f"Se eliminaron las filas con fechas inválidas. Filas restantes: {len(df)}")

    # --- 2. Procesamiento de columnas de Unidades (SKU) ---
    logger.info("Identificando y procesando columnas de SKU.")
    sku_columns = [col for col in df.columns if col.startswith("Unidades")]
    logger.debug(f"Columnas SKU identificadas: {sku_columns}") # DEBUG es más detallado
    if not sku_columns:
        logger.error("No se encontraron columnas de SKU que comiencen con 'Unidades'. Finalizando ejecución.")
        return pd.DataFrame() # Devolver un DF vacío si no hay nada que procesar

    logger.info(f"Convirtiendo {len(sku_columns)} columnas de SKU a tipo numérico.")
    df[sku_columns] = df[sku_columns].apply(pd.to_numeric, errors="coerce").fillna(0)

    # --- 3. Cálculo de stock ---
    logger.info("Iniciando el cálculo de stock por fecha y producto.")
    resumen_lista = []
    
    # Agrupar por fecha. Es más eficiente que iterar todo el DataFrame
    for fecha, grupo in df.groupby("Fecha"):
        for sku in sku_columns:
            # Usar .loc para un filtrado más explícito y eficiente
            movimientos = grupo.loc[:, ["Tipo de movimiento", sku]]
            
            stock_inicial = movimientos.loc[movimientos["Tipo de movimiento"] == "Stock inicial", sku].sum()
            ingresos = movimientos.loc[movimientos["Tipo de movimiento"] == "Ingreso", sku].sum()
            ventas = movimientos.loc[movimientos["Tipo de movimiento"] == "Salida", sku].sum()

            stock_final = stock_inicial + ingresos - ventas

            resumen_lista.append({
                "Fecha": fecha, # Mantenemos el objeto datetime por ahora
                "Producto": sku.replace("Unidades - ", ""),
                "Stock Inicial": int(stock_inicial),
                "Ingresos": int(ingresos),
                "Ventas": int(ventas),
                "Stock Final": int(stock_final)
            })
    
    logger.info(f"Cálculo de stock completado. Se generaron {len(resumen_lista)} registros.")

    # --- 4. Creación y retorno del DataFrame final ---
    if not resumen_lista:
        logger.warning("No se generó ningún dato en el resumen. Devolviendo DataFrame vacío.")
        return pd.DataFrame()

    logger.info("Creando y ordenando el DataFrame de resumen final.")
    resumen = pd.DataFrame(resumen_lista)
    
    # Formatear la fecha a string al final, para mantener el tipo correcto durante el ordenamiento
    resumen_ordenado = resumen.sort_values(by="Fecha")
    resumen_ordenado["Fecha"] = resumen_ordenado["Fecha"].dt.strftime("%d/%m/%Y")
    
    logger.info(f"Transformación finalizada exitosamente. DataFrame final con {len(resumen_ordenado)} filas.")
    
    return resumen_ordenado


def transformar_y_filtrar_datos_ventas_vs_ppto(df: pd.DataFrame,semanas: int):
    """Cambia el nombre de las columnas necesarias y se filtra por las n semanas últimas
    arg:
        df = dataframe extraido del sql server
        semanas = últimas semanas que se quiere filtrar
    """

    rename_columns = {
        "numSemana":"Semana",
        "idPeriodo":"Año",
        "PorcCumplimientoVenta":"Cumplimiento",
        "VentaReal":"Ventas Totales (S/)"
    }
    df = df.rename(columns = rename_columns)
    df["Semana_Año"] = df["Año"].astype(str) + " - Sem" + df["Semana"].astype(str)
    selec_columns = [
        'Semana_Año', 'ImporteProyectadoSemana', 'Ventas Totales (S/)',
        'Cumplimiento', 'Semana', 'Año'
    ]
    df = df[selec_columns]
    #filtrar
    fecha_actual = datetime.now()
    año_iso, numero_semana, _ = fecha_actual.isocalendar()
    df_filtrado = df[
        (df['Año'] == año_iso) & 
        (df['Semana'] <= numero_semana) & 
        (df['Semana'] >= numero_semana - semanas)
    ]
    return df_filtrado