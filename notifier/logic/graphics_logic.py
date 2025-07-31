# notifier/logic/graphics_logic.py
"""
Módulo dedicado exclusivamente a la lógica de generación de gráficos.
Toma DataFrames procesados y devuelve representaciones visuales.
"""
import pandas as pd
import base64
import plotly.graph_objects as go
import io
import logging
from datetime import datetime
import os
import tempfile

# --- FUNCIONES PRIVADAS (AYUDANTES INTERNOS DEL MÓDULO) ---

def _get_fillcolor(cumplimiento):
    """Determina el color de relleno basado en el porcentaje de cumplimiento."""
    if cumplimiento < 100:
        return "rgba(191, 48, 48, 0.4)"  # Rojo
    else:
        return "rgba(85, 150, 47, 0.4)"  # Verde

def _procesar_datos_para_grafico(df_semanal):
    """
    Prepara los datos del reporte semanal, agrupándolos y calculando
    el cumplimiento para que estén listos para graficar.
    """
    logging.info("Procesando datos para el gráfico semanal...")
    df = df_semanal.dropna(subset=['Año', 'Semana']).copy()

    ventas_agrupadas = df.groupby(["Año", "Semana"], as_index=False)["Ventas Totales (S/)"].sum()
    presupuesto_agrupado = df.groupby(["Año", "Semana"], as_index=False)["Importe Total Semanal"].first()

    ventas_agrupadas["Semana_Año"] = ventas_agrupadas["Año"].astype(str) + " - Sem" + ventas_agrupadas["Semana"].astype(str)
    presupuesto_agrupado["Semana_Año"] = presupuesto_agrupado["Año"].astype(str) + " - Sem" + presupuesto_agrupado["Semana"].astype(str)

    ventas_agrupadas = ventas_agrupadas.sort_values(["Año", "Semana"])
    presupuesto_agrupado = presupuesto_agrupado.sort_values(["Año", "Semana"])

    df_combinado = pd.merge(ventas_agrupadas, presupuesto_agrupado, on='Semana_Año', suffixes=('_real', '_presupuesto'))
    df_combinado['Cumplimiento'] = (df_combinado['Ventas Totales (S/)'] / df_combinado['Importe Total Semanal'] * 100).round(1)
    
    logging.info("Datos para el gráfico procesados exitosamente.")
    return df_combinado

def _generar_figura_plotly(df_combinado):
    """Crea el objeto de la figura de Plotly con las barras y anotaciones."""
    logging.info("Generando figura de Plotly...")
    fig = go.Figure()

    # Barra de presupuesto (base)
    fig.add_trace(go.Bar(
        x=df_combinado['Semana_Año'],
        y=df_combinado['Importe Total Semanal'],
        name='Presupuestado',
        marker_color="rgba(200, 200, 200, 0.6)",
        text=df_combinado['Importe Total Semanal'].apply(lambda x: f"S/ {x:,.0f}"),
        marker=dict(cornerradius=8)
    ))

    # Barra real
    fig.add_trace(go.Bar(
        x=df_combinado['Semana_Año'],
        y=df_combinado['Ventas Totales (S/)'],
        name='Real',
        marker_color='rgb(128, 128, 128)',
        text=df_combinado['Ventas Totales (S/)'].apply(lambda x: f"S/ {x/1000:,.1f}K"),
        textfont=dict(color='black', family="Arial")
    ))

    # Áreas de diferencia y anotaciones de cumplimiento
    for _, row in df_combinado.iterrows():
        y_annotation = row['Importe Total Semanal']
        text_color = 'red'
        yshift = 10
        if row['Cumplimiento'] >= 100:
            y_annotation = row['Ventas Totales (S/)']
            text_color = 'green'
        else: # Si el cumplimiento es menor a 100, se añade el rectángulo rojo
             fig.add_shape(type="rect", xref="x", yref="y",
                x0=row.name - 0.2, x1=row.name + 0.2,
                y0=row['Ventas Totales (S/)'], y1=row['Importe Total Semanal'],
                fillcolor=_get_fillcolor(row['Cumplimiento']),
                line_width=0
            )

        fig.add_annotation(
            x=row['Semana_Año'], y=y_annotation,
            text=f"{row['Cumplimiento']}%",
            showarrow=False, yshift=yshift,
            font=dict(color=text_color, weight="bold")
        )

    # Configuración del layout
    fig.update_layout(
        barmode='overlay',
        xaxis=dict(
            tickvals=df_combinado.index,
            ticktext=[f"Sem. {sem}<br>{año}" for sem, año in zip(df_combinado['Semana_real'], df_combinado['Año_real'])],
            tickangle=0, tickfont=dict(size=12)
        ),
        yaxis=dict(title=None, tickfont=dict(size=14)),
        plot_bgcolor="whitesmoke",
        paper_bgcolor="whitesmoke",
        legend=dict(font=dict(size=12), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=60, r=80, t=80, b=100),
        height=600, width=1200
    )
    logging.info("Figura de Plotly generada.")
    return fig

def _generar_imagen_base64(fig):
    """Convierte una figura de Plotly en una imagen PNG codificada en base64."""
    logging.info("Convirtiendo gráfico a imagen base64...")
    img_buffer = io.BytesIO()
    # Kaleido es necesario aquí, por eso lo añadimos en requirements.txt
    fig.write_image(img_buffer, format="png", scale=2) # scale=2 para mayor resolución
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    logging.info("Imagen base64 generada.")
    return img_base64

def _save_base64_image_to_temp(img_base64, filename_prefix="grafico_ventas"):
    """
    Guarda una imagen base64 en el directorio temporal de Cloud Run
    
    Args:
        img_base64 (str): String base64 de la imagen
        filename_prefix (str): Prefijo para el nombre del archivo
    
    Returns:
        str: Ruta completa del archivo guardado
    """
    try:
        # Decodificar base64
        img_data = base64.b64decode(img_base64)
        
        # Crear nombre único para el archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{filename_prefix}_{timestamp}.png"
        
        # Obtener directorio temporal (Cloud Run usa /tmp)
        temp_dir = tempfile.gettempdir()  # En Cloud Run esto será /tmp
        file_path = os.path.join(temp_dir, filename)
        
        # Guardar archivo
        with open(file_path, 'wb') as f:
            f.write(img_data)
        
        logging.info(f"Imagen guardada en: {file_path}")
        return file_path
        
    except Exception as e:
        logging.error(f"Error al guardar imagen en temp: {str(e)}")
        raise e

# --- FUNCIÓN PÚBLICA (LA ÚNICA QUE SE LLAMA DESDE FUERA) ---

def crear_grafico_real_vs_ppto_base64(df_reporte_semanal):
    """
    Función principal del módulo. Orquesta la creación del gráfico.
    
    Args:
        df_reporte_semanal (pd.DataFrame): El DataFrame generado por 
                                          report_logic.generar_reporte_semanal_ventas_vs_ppto.

    Returns:
        str: La imagen del gráfico codificada en base64, lista para ser usada en un email.
    """
    if df_reporte_semanal.empty:
        logging.warning("El DataFrame para el gráfico está vacío. No se generará ninguna imagen.")
        return None

    df_procesado = _procesar_datos_para_grafico(df_reporte_semanal)
    figura = _generar_figura_plotly(df_procesado)
    imagen_base64 = _generar_imagen_base64(figura)
    return imagen_base64

def crear_grafico_y_guardar_en_temp(df_reporte_semanal, filename_prefix="grafico_ventas"):
    """
    Crea el gráfico y lo guarda en el directorio temporal de Cloud Run.
    Args:
        df_reporte_semanal (pd.DataFrame): El DataFrame del reporte semanal
        filename_prefix (str): Prefijo para el nombre del archivo
    Returns:
        str: ruta_archivo_temp
    """
    if df_reporte_semanal.empty:
        logging.warning("El DataFrame para el gráfico está vacío. No se generará ninguna imagen.")
        return None

    df_procesado = _procesar_datos_para_grafico(df_reporte_semanal)
    figura = _generar_figura_plotly(df_procesado)
    imagen_base64 = _generar_imagen_base64(figura)
    ruta_temp = _save_base64_image_to_temp(imagen_base64, filename_prefix)
    return ruta_temp