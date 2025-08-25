import pandas as pd
import logging
# Configurar logging
logger = logging.getLogger(__name__)
def tabla_html(df):
    df = df.drop(columns=[])

    html = '<table style="width: 100%; border-collapse: collapse; font-family: Calibri; font-size: 10pt;">'
    
    # Encabezados
    html += '<tr style="background-color: #003366; color: white; font-weight: bold; text-align: center;">'
    for col in df.columns:
        col_style = "padding: 8px; border: 1px solid #dddddd; text-align: center; white-space: normal;"
        html += f'<th style="{col_style}">{col if col not in ["%.1"] else "%"}</th>'
    html += '</tr>'
    
    # Columnas específicas a ajustar
    columnas_ajustadas = ["Cantidad Total (kg)", "Precio Prom", "Ventas Totales (S/)", "Participación (%)"]

    # Filas
    for _, row in df.iterrows():
        html += '<tr>'
        for col, value in zip(df.columns, row):
            col_style = "padding: 8px; border: 1px solid #dddddd; text-align: center;"
            
            if col == "Categoría":
                col_style += " width: 200px;"  # Más ancho para Categoría
            elif col in columnas_ajustadas:
                col_style += " white-space: nowrap; max-width: 150px; overflow: hidden; text-overflow: ellipsis;"
            elif col == df.columns[0]:
                col_style += " text-align: left;"  # Primera columna alineada a la izquierda

            html += f'<td style="{col_style}">{value}</td>'
        
        html += '</tr>'
    
    html += '</table>'
    return html