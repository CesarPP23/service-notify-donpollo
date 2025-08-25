import pandas as pd
import logging
# Configurar logging
logger = logging.getLogger(__name__)
def generar_comentarios_producto(df):
    # Convertir las columnas a valores numéricos
    df["Cantidad Total (kg)"] = df["Cantidad Total (kg)"].astype(float)
    df["Ventas Totales (S/)"] = df["Ventas Totales (S/)"].str.replace("S/ ", "").str.replace(",", "").astype(float)
    df_filtered = df[df['Categoría'] != "Total"]
    # Sumar los valores
    total_ventas = df_filtered["Ventas Totales (S/)"].sum()
    total_kg = df_filtered["Cantidad Total (kg)"].sum()
    precio_prom = total_ventas/total_kg
    # Formatear los resultados
    total_ventas_formato = f"S/ {total_ventas:,.0f}"
    total_kg_formato = f"{total_kg:,.0f} kg"
    precio_prom = f"S/ {precio_prom:,.2f}"

    return total_ventas_formato,total_kg_formato,precio_prom