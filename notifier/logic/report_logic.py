# notifier/logic/report_logic.py (VERSIÓN FINAL CORREGIDA)
"""
Módulo dedicado exclusivamente a la lógica de negocio:
Leer dataframes desde rutas de archivos y transformarlos para generar los reportes.
"""
import pandas as pd
import numpy as np
from datetime import datetime
import calendar
import gspread
from google.auth import default # Usamos la autenticación por defecto del entorno
import logging

from notifier.config import MESES_DICT, ACCESOS_GSPREAD

# --- FUNCIÓN AUXILIAR DE LECTURA ---
def leer_excel(ruta, **kwargs):
    try:
        return pd.read_excel(ruta, **kwargs)
    except FileNotFoundError:
        logging.error(f"Archivo no encontrado en la ruta temporal: {ruta}")
        raise
    except Exception as e:
        logging.error(f"Error al leer el archivo Excel {ruta}: {e}")
        raise

# --- LÓGICA PARA GOOGLE SHEETS (CORREGIDA) ---
def get_df_from_gspread(form):
    """
    Se autentica con G-Sheets usando las credenciales automáticas del entorno
    de Google Cloud y devuelve un DataFrame.
    """
    logging.info(f"Accediendo a Google Sheet para '{form}' usando credenciales del entorno...")
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds, _ = default(scopes=scopes)
        client = gspread.authorize(creds)
        
        SHEET_ID = ACCESOS_GSPREAD[form]["SHEET_ID"]
        spreadsheet = client.open_by_key(SHEET_ID)
        
        data_formulario = spreadsheet.sheet1.get_all_values()
        headers = data_formulario[0]
        df = pd.DataFrame(data_formulario[1:], columns=headers)
        logging.info("DataFrame obtenido de Google Sheet exitosamente.")
        return df
    except Exception as e:
        logging.error(f"No se pudo conectar o leer desde Google Sheets. Error: {e}")
        raise


def generar_resumen_stock(df):
    df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
    sku_columns = [col for col in df.columns if col.startswith("Unidades")]
    df[sku_columns] = df[sku_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    resumen_lista = []
    for fecha, grupo in df.groupby("Fecha"):
        for sku in sku_columns:
            stock_inicial = grupo[grupo["Tipo de movimiento"] == "Stock inicial"][sku].sum()
            ingresos = grupo[grupo["Tipo de movimiento"] == "Ingreso"][sku].sum()
            ventas = grupo[grupo["Tipo de movimiento"] == "Salida"][sku].sum()
            stock_final = stock_inicial + ingresos - ventas
            resumen_lista.append({
                "Fecha": fecha.strftime("%d/%m/%Y"), "Producto": sku.replace("Unidades - ", ""),
                "Stock Inicial": int(stock_inicial), "Ingresos": int(ingresos),
                "Ventas": int(ventas), "Stock Final": int(stock_final)
            })
    return pd.DataFrame(resumen_lista).sort_values(by="Fecha")

# --- LÓGICA DE REPORTES DE VENTAS Y PRESUPUESTO ---

def format_ventas(df):
    columnas = {
        "Líneas de factura/Fecha": "fecha", "Líneas de factura/Número": "nro_comprobante",
        "Líneas de factura/Contacto/Tipo de Identificación": "tipo_id_cliente",
        "Líneas de factura/Contacto/NIT, CUIT, RIF, RUT, RNC, TIN, RUC, RFC, RTN": "id_cliente",
        "Líneas de factura/Contacto": "nombre_cliente", "Líneas de factura/Cantidad": "cantidad",
        "Líneas de factura/Producto/Nombre": "nombre_producto", "Líneas de factura/Precio unitario": "precio_unitario",
        "Líneas de factura/Producto/Referencia interna": "id_producto",
        "Líneas de factura/Asiento contable/Creado el": "FechaHora"
    }
    df = df.rename(columns=columnas)
    df['FechaHora'] = pd.to_datetime(df['FechaHora'])
    df['Hora_HHMM'] = df['FechaHora'].dt.strftime('%H:%M')
    return df

def filter_nc_in_ventas(df_nc, df_ventas):
    df_nc["Líneas de factura/Referencia"] = df_nc["Líneas de factura/Referencia"].astype(str)
    df_ventas["nro_comprobante"] = df_ventas["nro_comprobante"].astype(str)
    df_ventas["id_producto"] = df_ventas["id_producto"].astype(str)
    df_ventas['pxq_prev'] = df_ventas['cantidad'] * df_ventas['precio_unitario']

    def calcular_nc_valor(row):
        id_boleta = row["nro_comprobante"]
        id_producto = row["id_producto"]
        nc_filtradas = df_nc[(df_nc["Líneas de factura/Referencia"].str.contains(id_boleta, na=False, case=False)) & (df_nc["id_producto"] == id_producto)]
        return (nc_filtradas["precio_unitario"] * nc_filtradas["cantidad"]).sum()

    df_ventas["NC_Valor"] = df_ventas.apply(calcular_nc_valor, axis=1)
    df_ventas['pxq'] = df_ventas['pxq_prev'] - df_ventas['NC_Valor']
    return df_ventas

def generar_bd_ventas_formateada(rutas_locales):
    """Genera la BD de ventas leyendo los archivos de las rutas locales (/tmp)."""
    df_nc = leer_excel(rutas_locales["nc"])
    df_ventas = leer_excel(rutas_locales["ventas"])
    df_nc = format_ventas(df_nc)
    df_ventas = format_ventas(df_ventas)
    return filter_nc_in_ventas(df_nc, df_ventas)

def transformar_ventas_diario_x_producto(df):
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["Año"] = df["fecha"].dt.isocalendar().year
    df = df.sort_values(by="FechaHora")
    df_producto = df.groupby(["fecha", "Año", "nombre_producto"]).agg(
        cantidad_total_kg=("cantidad", "sum"),
        ventas_totales_soles=("pxq", "sum"),
        nro_comprobantes=("nro_comprobante", "nunique"),
        fecha_hora_ultima_compra=("FechaHora", "last")
    ).reset_index()
    df_producto.columns = ["Fecha", "Año", "Nombre_Producto", "Cantidad Total (kg)", "Ventas Totales (S/)", "Número de Comprobantes", "FechaHora última compra"]
    return df_producto

def transformar_ventas_semanal(df):
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["Año"] = df["fecha"].dt.isocalendar().year
    df["Semana"] = df["fecha"].dt.isocalendar().week
    df["Semana_Periodo"] = df["fecha"].dt.to_period("W-SUN")
    df_semanal = df.groupby(["Semana_Periodo", "Año", "Semana", "nombre_producto"]).agg(
        cantidad_total_kg=("cantidad", "sum"),
        ventas_totales_soles=("pxq", "sum"),
        nro_comprobantes=("nro_comprobante", "nunique")
    ).reset_index()
    df_semanal.columns = ["Semana_Periodo", "Año", "Semana", "Nombre_Producto", "Cantidad Total (kg)", "Ventas Totales (S/)", "Número de Comprobantes"]
    return df_semanal

def transformar_presupuesto_diario(rutas_locales):
    df_ppto = leer_excel(rutas_locales["presupuesto"])
    df_ppto_micasero = df_ppto[df_ppto['Línea de Negocio'] == "Mi casero"].copy()
    df_ppto_micasero["Mes_Num"] = df_ppto_micasero["Mes"].map(MESES_DICT)
    df_ppto_micasero["Año"] = df_ppto_micasero["Año"].astype(int)
    df_ppto_micasero["Mes_Num"] = df_ppto_micasero["Mes_Num"].astype(int)
    df_ppto_micasero["Dias_Mes"] = df_ppto_micasero.apply(lambda row: calendar.monthrange(row["Año"], row["Mes_Num"])[1], axis=1)
    df_ppto_micasero["Importe Total Diario"] = df_ppto_micasero["Importe"] / df_ppto_micasero["Dias_Mes"]
    registros = []
    for _, row in df_ppto_micasero.iterrows():
        for dia in range(1, row["Dias_Mes"] + 1):
            fecha = datetime(row["Año"], row["Mes_Num"], dia)
            registros.append({"Fecha": fecha, "Importe Total Diario": row["Importe Total Diario"]})
    return pd.DataFrame(registros)

def transformar_presupuesto_semanal(df_ppto_diario):
    df_ppto_diario["Semana_Periodo"] = df_ppto_diario["Fecha"].dt.to_period("W-SUN")
    df_ppto_diario["Numero_Semana"] = df_ppto_diario["Fecha"].dt.isocalendar().week
    df_ppto_semanal = df_ppto_diario.groupby(["Semana_Periodo", "Numero_Semana"])["Importe Total Diario"].sum().reset_index()
    df_ppto_semanal.rename(columns={"Importe Total Diario": "Importe Total Semanal"}, inplace=True)
    return df_ppto_semanal

def generar_reporte_semanal_ventas_vs_ppto(rutas_locales):
    df_ppto_diario = transformar_presupuesto_diario(rutas_locales)
    df_ppto_semanal = transformar_presupuesto_semanal(df_ppto_diario)
    df_ventas = generar_bd_ventas_formateada(rutas_locales)
    df_ventas_semanal = transformar_ventas_semanal(df_ventas)
    df_merge = pd.merge(df_ventas_semanal, df_ppto_semanal, how='left', on='Semana_Periodo')
    df_merge['Semana_Periodo'] = df_merge['Semana_Periodo'].astype(str)
    df_merge['Fecha_Inicio_Semana'] = df_merge['Semana_Periodo'].str.split('/').str[0]
    df_merge['Fecha_Inicio_Semana'] = pd.to_datetime(df_merge['Fecha_Inicio_Semana'], errors='coerce')
    semanas_recientes = df_merge[['Semana_Periodo', 'Fecha_Inicio_Semana']].drop_duplicates().sort_values('Fecha_Inicio_Semana', ascending=False).head(10)['Semana_Periodo'].tolist()
    return df_merge[df_merge['Semana_Periodo'].isin(semanas_recientes)].sort_values(['Fecha_Inicio_Semana', 'Nombre_Producto']).reset_index(drop=True)

def generar_tabla_producto(rutas_locales):
    df_ventas = generar_bd_ventas_formateada(rutas_locales)
    df_ventas_producto = transformar_ventas_diario_x_producto(df_ventas)
    last_date = df_ventas_producto['Fecha'].max()
    df_ultimo_dia = df_ventas_producto[df_ventas_producto['Fecha'] == last_date].reset_index(drop=True)
    df_ultimo_dia['Precio'] = df_ultimo_dia['Ventas Totales (S/)'] / df_ultimo_dia['Cantidad Total (kg)']
    total_ventas = df_ultimo_dia['Ventas Totales (S/)'].sum()
    df_ultimo_dia['Participación (%)'] = (df_ultimo_dia['Ventas Totales (S/)'] / total_ventas) * 100
    df_ultimo_dia['Categoría'] = np.where(df_ultimo_dia['Nombre_Producto'].str.contains(r'POLLO C/M|POLLO S/M', regex=True, case=False), '1. Pollo entero', '2. Adicional')
    df_ultimo_dia['Ticket promedio'] = df_ultimo_dia['Ventas Totales (S/)'] / df_ultimo_dia['Número de Comprobantes']
    df_ultimo_dia['Última Compra (hh:mm)'] = df_ultimo_dia['FechaHora última compra'].dt.strftime('%H:%M')
    df_ultimo_dia = df_ultimo_dia.rename(columns={'Nombre_Producto': 'Nombre Producto', 'Número de Comprobantes': 'Nro ventas'})
    df_ultimo_dia = df_ultimo_dia.sort_values('Participación (%)', ascending=False).reset_index(drop=True)
    return df_ultimo_dia[['Nombre Producto', 'Categoría', 'Participación (%)', 'Cantidad Total (kg)', 'Precio', 'Ventas Totales (S/)', 'Nro ventas', 'Ticket promedio', 'Última Compra (hh:mm)']]

def formatear_tabla_producto(df_ultimo_dia):
    df_formateado = df_ultimo_dia[['Nombre Producto', 'Categoría', 'Participación (%)', 'Cantidad Total (kg)', 'Precio', 'Ventas Totales (S/)', 'Última Compra (hh:mm)']].copy()
    df_formateado['Ventas Totales (S/)'] = df_formateado['Ventas Totales (S/)'].apply(lambda x: f"S/ {x:,.2f}")
    df_formateado['Participación (%)'] = df_formateado['Participación (%)'].apply(lambda x: f"{x:.2f}%")
    df_formateado['Precio'] = df_formateado['Precio'].apply(lambda x: f"S/ {x:,.2f}")
    df_formateado['Cantidad Total (kg)'] = df_formateado['Cantidad Total (kg)'].round(2)
    return df_formateado

def formatear_tabla_categoria(df_categoria_final):
    df_formateado = df_categoria_final.copy()
    df_formateado['Ventas Totales (S/)'] = df_formateado['Ventas Totales (S/)'].apply(lambda x: f"S/ {x:,.2f}")
    df_formateado['Participación (%)'] = df_formateado['Participación (%)'].apply(lambda x: f"{x:.2f}%")
    df_formateado['Precio'] = df_formateado['Precio'].apply(lambda x: f"S/ {x:,.2f}")
    df_formateado['Cantidad Total (kg)'] = df_formateado['Cantidad Total (kg)'].round(2)
    df_formateado['Ticket promedio'] = df_formateado['Ticket promedio'].apply(lambda x: f"S/ {x:,.2f}")
    return df_formateado

def generar_tabla_categoria(df_reporte_diario):
    df_categoria = df_reporte_diario.groupby(["Categoría"]).agg(
        participacion_porc=("Participación (%)", "sum"),
        cantidad_kg=("Cantidad Total (kg)", "sum"),
        ventas_soles=("Ventas Totales (S/)", "sum"),
        nro_ventas=("Nro ventas", "sum")
    ).reset_index()
    df_categoria['Precio'] = df_categoria['ventas_soles'] / df_categoria['cantidad_kg']
    df_categoria['Ticket promedio'] = df_categoria['ventas_soles'] / df_categoria['nro_ventas']
    return df_categoria[['Categoría', 'participacion_porc', 'cantidad_kg', 'Precio', 'ventas_soles', 'nro_ventas', 'Ticket promedio']]

def generar_reporte_diario_producto_formateado(rutas_locales):
    df_1 = generar_tabla_producto(rutas_locales)
    return formatear_tabla_producto(df_1)

def generar_reporte_diario_categoria_formateado(rutas_locales):
    df = generar_tabla_producto(rutas_locales)
    df_1 = generar_tabla_categoria(df)
    total_cantidad = df_1["cantidad_kg"].sum()
    total_ventas = df_1["ventas_soles"].sum()
    total_nro_ventas = df_1["nro_ventas"].sum()
    total_precio = total_ventas / total_cantidad if total_cantidad > 0 else 0
    total_ticket_promedio = total_ventas / total_nro_ventas if total_nro_ventas > 0 else 0
    fila_total = pd.DataFrame({
        "Categoría": ["Total"], "participacion_porc": [100],
        "cantidad_kg": [total_cantidad], "Precio": [total_precio],
        "ventas_soles": [total_ventas], "nro_ventas": [total_nro_ventas],
        "Ticket promedio": [total_ticket_promedio]
    })
    df_final = pd.concat([df_1, fila_total], ignore_index=True)
    df_final.columns = ['Categoría', 'Participación (%)', 'Cantidad Total (kg)', 'Precio', 'Ventas Totales (S/)', 'Nro ventas', 'Ticket promedio']
    return formatear_tabla_categoria(df_final)

def generar_reporte_diario_und_pollos(rutas_locales):
    # ¡CORRECCIÓN! Ahora llama a la función correcta 'get_df_from_gspread'
    # que usa la autenticación automática y ya no necesita la ruta al archivo .json
    df_movimientos = get_df_from_gspread('form_mov_pollos')
    
    df_resumen = generar_resumen_stock(df_movimientos)
    df_resumen['Fecha'] = pd.to_datetime(df_resumen['Fecha'], dayfirst=True)
    df_ventas_bd = generar_bd_ventas_formateada(rutas_locales)
    df_ventas_bd['fecha'] = pd.to_datetime(df_ventas_bd['fecha'], dayfirst=True)
    last_date = df_ventas_bd['fecha'].max()
    df_resumen_filtrado = df_resumen[df_resumen['Fecha'] == last_date].copy()
    
    if df_resumen_filtrado.empty:
        logging.warning("No se encontraron datos de stock para la última fecha de venta.")
        return pd.DataFrame(), "0 UND"

    df_resumen_filtrado['Fecha'] = df_resumen_filtrado['Fecha'].dt.strftime("%d/%m/%Y")
    df_ventas_bd['fecha_str'] = df_ventas_bd['fecha'].dt.strftime("%d/%m/%Y")
    
    df_merged = df_resumen_filtrado.merge(
        df_ventas_bd[['fecha_str', 'nombre_producto', 'Hora_HHMM']],
        left_on=['Fecha', 'Producto'], right_on=['fecha_str', 'nombre_producto'], how='left'
    )
    df_merged = df_merged.sort_values(by=['Producto', 'Hora_HHMM'], ascending=True).drop_duplicates(subset=['Producto'], keep='last')
    und_vendidas_pollos = df_merged["Ventas"].sum()
    comentario_und_pollos = f"{und_vendidas_pollos:,.0f} UND"
    df_final = df_merged[['Fecha', 'Producto', 'Stock Inicial', 'Ingresos', 'Ventas', 'Stock Final', 'Hora_HHMM']].rename(columns={'Hora_HHMM': 'Última Compra (hh:mm)'})
    return df_final, comentario_und_pollos


def generar_comentarios_producto(rutas_locales):
    df_categoria_formateado = generar_reporte_diario_categoria_formateado(rutas_locales)
    total_row = df_categoria_formateado[df_categoria_formateado['Categoría'] == 'Total']
    total_ventas_str = total_row['Ventas Totales (S/)'].iloc[0]
    total_kg = float(total_row['Cantidad Total (kg)'].iloc[0])
    precio_prom_str = total_row['Precio'].iloc[0]
    total_kg_formato = f"{total_kg:,.2f} kg"
    return total_ventas_str, total_kg_formato, precio_prom_str

def df_a_html(df):
    """Convierte un DataFrame de pandas a una tabla HTML con estilos."""
    # (Pega aquí tu función df_a_html, sin cambios)
    html = '<table style="width: 100%; border-collapse: collapse; font-family: Calibri; font-size: 10pt;">'
    html += '<tr style="background-color: #003366; color: white; font-weight: bold; text-align: center;">'
    for col in df.columns:
        html += f'<th style="padding: 8px; border: 1px solid #dddddd; text-align: center;">{col}</th>'
    html += '</tr>'
    for _, row in df.iterrows():
        html += '<tr>'
        for val in row:
            html += f'<td style="padding: 8px; border: 1px solid #dddddd; text-align: center;">{val}</td>'
        html += '</tr>'
    html += '</table>'
    return html

def _procesar_datos_semanales_vs_ppto(df_semanal_raw):
    """
    Función privada que toma el reporte semanal y lo procesa para obtener el cumplimiento.
    Basado en tu función 'procesar_datos'.
    """
    df = df_semanal_raw.dropna(subset=['Año', 'Semana']).copy()
    ventas_semanales = df.groupby(["Año", "Semana"], as_index=False)["Ventas Totales (S/)"].sum()
    presupuesto = df.groupby(["Año", "Semana"], as_index=False)["Importe Total Semanal"].first()
    ventas_semanales["Semana_Año"] = ventas_semanales["Año"].astype(str) + " - Sem" + ventas_semanales["Semana"].astype(str)
    presupuesto["Semana_Año"] = presupuesto["Año"].astype(str) + " - Sem" + presupuesto["Semana"].astype(str)
    ventas_semanales = ventas_semanales.sort_values(["Año", "Semana"]).reset_index(drop=True)
    presupuesto = presupuesto.sort_values(["Año", "Semana"]).reset_index(drop=True)
    df_combinado = pd.merge(ventas_semanales, presupuesto, on=['Semana_Año'], suffixes=('_real', '_presupuesto'))
    df_combinado['Cumplimiento'] = (df_combinado['Ventas Totales (S/)'] / df_combinado['Importe Total Semanal'] * 100).round(1)
    return df_combinado

def generar_comentario_cumplimiento_ppto(rutas_locales):
    """
    Genera el comentario de texto del cumplimiento del presupuesto de la última semana.
    Basado en tu función 'generar_comentarios_ppto'.
    """
    # 1. Genera el reporte semanal base, que es el input necesario
    df_reporte_semanal = generar_reporte_semanal_ventas_vs_ppto(rutas_locales)
    
    # 2. Procesa esos datos para calcular el cumplimiento
    df_combinado = _procesar_datos_semanales_vs_ppto(df_reporte_semanal)
    
    if df_combinado.empty:
        return "N/A"

    # 3. Filtra la última semana y calcula el valor
    ultima_semana = df_combinado['Semana_real'].iloc[-1]
    df_filtrado = df_combinado[df_combinado['Semana_real'] == ultima_semana]
    cumplimiento_coment = df_filtrado['Cumplimiento'].sum()
    cumplimiento_coment_text = f"{cumplimiento_coment:,.1f}%"
    return cumplimiento_coment_text