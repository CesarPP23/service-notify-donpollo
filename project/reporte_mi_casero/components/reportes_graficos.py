import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, Any
from utils.convertir_img_base64 import generar_imagen_base64
import logging
# Configurar logging
logger = logging.getLogger(__name__)

CHART_CONFIG = {
    "colors": {
        "primary": "#003366",  # Azul oscuro para la semana actual
        "secondary": "rgba(200, 200, 200, 0.8)",  # Gris para la semana anterior
        "positive": "rgb(85, 150, 47)",  # Verde
        "negative": "rgb(191, 48, 48)",  # Rojo
        "background": "whitesmoke",
        "grid": "lightgrey",
        "font_primary": "white",
        "font_secondary": "black",
    },
    "fonts": {
        "title_size": 20,
        "bar_label_size": 13,
        "annotation_size": 13,
    },
    "templates": {
        "bar_label": "S/ {value:.1f}K",
        "hover_anterior": "<b>%{x}</b><br>Sem. Anterior: S/ %{y:,.0f}<extra></extra>",
        "hover_actual": "<b>%{x}</b><br>Sem. Actual: S/ %{y:,.0f}<br>Diferencia: %{customdata:.2f}%<extra></extra>",
        "annotation": "<b>{value:.2f}%</b>",
    },
    "layout": {
        "title": "<b>Ventas Semanales: Actual vs. Anterior</b>",
        "yaxis_multiplier": 1.25,
        "annotation_yshift": 16,
    }
}

def crear_grafico_ventas_semanales(df: pd.DataFrame, config: Dict[str, Any] = CHART_CONFIG) -> go.Figure:
    """
    Genera un gráfico de barras comparativo de ventas semanales.

    Args:
        df (pd.DataFrame): DataFrame con columnas 'Dia', 'VentaSemanaAnterior',
                           'VentaSemanaActual', y 'DiferenciaPorcentaje'.
        config (Dict[str, Any]): Diccionario de configuración para el gráfico.

    Returns:
        go.Figure: Objeto Figure de Plotly listo para ser mostrado o guardado.
    """
    logger.info("Iniciando la generación del gráfico de ventas semanales.")
    
    # --- 1. Preparación de Datos ---
    df_sorted = df.copy()
    dias_ordenados = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    df_sorted['Dia'] = pd.Categorical(df_sorted['Dia'], categories=dias_ordenados, ordered=True)
    df_sorted = df_sorted.sort_values('Dia')
    # En caso sea 0 convertirlo en -

    # --- 2. Creación de la Figura ---
    fig = go.Figure()

    # Trazado para la Semana Anterior
    fig.add_trace(go.Bar(
        x=df_sorted['Dia'],
        y=df_sorted['VentaSemanaAnterior'],
        name='Semana Anterior',
        marker_color=config["colors"]["secondary"],
        text=df_sorted['VentaSemanaAnterior'].apply(lambda y: config["templates"]["bar_label"].format(value=y/1000)),
        textfont=dict(color=config["colors"]["font_secondary"], size=config["fonts"]["bar_label_size"]),
        hovertemplate=config["templates"]["hover_anterior"],
    ))

    # Trazado para la Semana Actual
    fig.add_trace(go.Bar(
        x=df_sorted['Dia'],
        y=df_sorted['VentaSemanaActual'],
        name='Semana Actual',
        marker_color=config["colors"]["primary"],
        text=df_sorted['VentaSemanaActual'].apply(lambda y: config["templates"]["bar_label"].format(value=y/1000)),
        textfont=dict(color=config["colors"]["font_primary"], size=config["fonts"]["bar_label_size"]),
        customdata=df_sorted['DiferenciaPorcentaje'],
        hovertemplate=config["templates"]["hover_actual"],
    ))

    # --- 3. Anotaciones de Diferencia ---
    for _, row in df_sorted.iterrows():
        color = config["colors"]["positive"] if row['DiferenciaPorcentaje'] >= 0 else config["colors"]["negative"]
        fig.add_annotation(
            x=row['Dia'],
            y=max(row['VentaSemanaAnterior'], row['VentaSemanaActual']),
            text=config["templates"]["annotation"].format(value=row['DiferenciaPorcentaje']),
            showarrow=False,
            font=dict(size=config["fonts"]["annotation_size"], color=color),
            yshift=config["layout"]["annotation_yshift"]
        )

    # --- 4. Configuración del Layout ---
    max_y_value = df_sorted[['VentaSemanaAnterior', 'VentaSemanaActual']].max().max()
    fig.update_layout(
        title=dict(text=config["layout"]["title"], x=0.5, font=dict(size=config["fonts"]["title_size"])),
        barmode='group',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor=config["colors"]["background"],
        paper_bgcolor=config["colors"]["background"],
        yaxis=dict(gridcolor=config["colors"]["grid"], title=None, showticklabels=False),
        xaxis=dict(title=None),
        yaxis_range=[0, float(max_y_value) * config["layout"]["yaxis_multiplier"]],
        margin=dict(t=80, b=20, l=20, r=20) # Ajuste de márgenes
    )
    
    logger.info("Gráfico generado exitosamente.")
    return fig

# Wrapper para generar la imagen (asumiendo que tienes la función en utils)
# from utils.convertir_img_base64 import generar_imagen_base64
def crear_imagen_ventas_semanales(df: pd.DataFrame) -> str:
    """
    Función principal que genera la imagen base64 del reporte comparativo de semanas.
    """
    figura = crear_grafico_ventas_semanales(df)
    return generar_imagen_base64(figura)

def crear_imagen_ventas_semanales_guardar(df: pd.DataFrame) -> None:
    """
    Función de prueba para aislar ÚNICAMENTE el guardado del archivo HTML.
    """
    print("📊 Generando el gráfico de ventas semanales...")
    figura = crear_grafico_ventas_semanales(df)
    
    # Ruta de destino
    nombre_archivo = r"D:\servicio-notificador-correo\index.html"
    
    print(f"--- INTENTANDO GUARDAR EN: {nombre_archivo} ---")
    
    try:
        # ÚNICA ACCIÓN: Guardar el archivo HTML
        figura.write_html(nombre_archivo)
        print(f"✅ COMANDO DE GUARDADO EJECUTADO. Revisa la ruta.")
        
    except Exception as e:
        # Si hay un error al guardar, se mostrará aquí
        print(f"❌ ERROR REAL AL GUARDAR: {e}")
        print("   Esto confirma un problema de permisos o de ruta inválida.")

    # La llamada a generar_imagen_base64 HA SIDO ELIMINADA para esta prueba.
    
