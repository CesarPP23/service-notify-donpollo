from datetime import datetime

# Importaciones de tus módulos
from service.conect_google_sheet import get_excel_stock_und
from service.conect_db import ReporteExecutor
from service.email_service import enviar_email_con_reintentos,enviar_email
from config.config import GOOGLE_SHEET_CREDENTIALS, ACCESOS_SHEET_GOOGLE, REPORTES_CONFIG, DB_CONFIG, DESTINATARIOS, SENDER_EMAIL,SMTP_SERVER,SMTP_PORT,PASSWORD
from utils.logs import main_loger
from data.transformar import format_table, transformar_y_filtrar_datos_ventas_vs_ppto, transformar_df_sheet_google
from data.generar_reporte_google import generar_reporte_diario_und_pollos
from data.generar_reporte_odoo import generar_comentarios_producto
from components.reportes_graficos import crear_imagen_ventas_semanales
from components.reporte_graficos_2 import crear_imagen_ventas_semanales_vs_ppto
from components.generar_tablas_html import tabla_html
from validators.validator_data import validar_movimientos_diarios_completos,DatosInvalidosError,validar_dataframe_no_vacio

def obtener_dataframes(fecha):
    executor = ReporteExecutor(db_config=DB_CONFIG, reportes_config=REPORTES_CONFIG)
    df_semanal_vs_ppto = executor.ejecutar_reporte('ventas_semanal_vs_ppto')
    df_ventas_x_sku = executor.ejecutar_reporte('ventas_x_sku', fecha=fecha)
    df_ventas_x_categoria = executor.ejecutar_reporte('ventas_x_categoria', fecha=fecha)
    df_ventas_x_diasem = executor.ejecutar_reporte('ventas_comparativo_x_semana_x_dia', fecha=fecha)
    df_ventas_unidades_google = get_excel_stock_und(
        form='form_mov_pollos',
        GOOGLE_SHEET_CREDENTIALS=GOOGLE_SHEET_CREDENTIALS,
        ACCESOS_SHEET_GOOGLE=ACCESOS_SHEET_GOOGLE
    )
    return (df_semanal_vs_ppto, df_ventas_x_sku, df_ventas_x_categoria, df_ventas_x_diasem, df_ventas_unidades_google)

def preparar_tablas_y_comentarios(df_ventas_x_sku, df_ventas_x_categoria, df_ventas_unidades_google, fecha):
    df_ventas_unidades_2 = transformar_df_sheet_google(df_ventas_unidades_google)
    df_ventas_unidades_final, comentario_und = generar_reporte_diario_und_pollos(
        df_und_google=df_ventas_unidades_2,
        df_ventas_odo_lastday=df_ventas_x_sku,
        fecha_objetivo=fecha
    )
    tabla_unidades_html = tabla_html(df_ventas_unidades_final)
    df_ventas_x_sku_final = format_table(df_ventas_x_sku)
    tabla_ventas_x_sku_html = tabla_html(df_ventas_x_sku_final)
    total_ventas_formato, total_kg_formato, precio_prom = generar_comentarios_producto(df_ventas_x_sku_final)
    df_ventas_x_categoria_final = format_table(df_ventas_x_categoria)
    tabla_ventas_x_categoria_html = tabla_html(df_ventas_x_categoria_final)
    return (tabla_unidades_html, tabla_ventas_x_categoria_html, tabla_ventas_x_sku_html,
            comentario_und, total_ventas_formato, total_kg_formato, precio_prom)

def preparar_graficos(df_ventas_x_diasem, df_semanal_vs_ppto):
    grafico_ventas_comp_semanas_bas64 = crear_imagen_ventas_semanales(df_ventas_x_diasem)
    df_ventas_sem_vs_ppto = transformar_y_filtrar_datos_ventas_vs_ppto(df_semanal_vs_ppto, semanas=10)
    grafico_ventas_comp_sem_ppto_bas64 = crear_imagen_ventas_semanales_vs_ppto(df_ventas_sem_vs_ppto)
    return grafico_ventas_comp_semanas_bas64, grafico_ventas_comp_sem_ppto_bas64

def construir_cuerpo_email(tabla_unidades_html, tabla_ventas_x_categoria_html, tabla_ventas_x_sku_html,
                          comentario_und, total_ventas_formato, total_kg_formato, precio_prom,
                          grafico_ventas_comp_semanas_bas64, grafico_ventas_comp_sem_ppto_bas64):
    return f"""
    <p>Estimados,</p>
    <p>Resumen de ventas del día:</p>
    <ul style="list-style-type: none; padding-left: 0; margin: 0;">
        <li><b>Pollos Vendidos:</b> {comentario_und}</li>
        <li><b>Ingresos Totales:</b> {total_ventas_formato}</li>
        <li><b>Volumen Total:</b> {total_kg_formato}</li>
        <li><b>Precio Promedio:</b> {precio_prom}</li>
    </ul>
    <p>
        📊 Link del Dashboard: 
        <a href="" 
        target="_blank" style="color: #0078D4; text-decoration: none;">
        Ver en Power BI
        </a>
    </p>
    <img src="data:image/png;base64,{grafico_ventas_comp_semanas_bas64}">
    <p>A continuación, los reportes:</p>
    <h3>📌 Resumen de Stock (UND Pollos)</h3>
    {tabla_unidades_html}
    <br>
    <h3>📌 Resumen de Ventas</h3>
    {tabla_ventas_x_categoria_html}
    <br>
    <h3>📌 Detalle de Ventas por Producto</h3>
    {tabla_ventas_x_sku_html}
    <br>
    <h3>📌 Real vs Ppto por semana</h3>
    <img src="data:image/png;base64,{grafico_ventas_comp_sem_ppto_bas64}" alt="Real vs Ppto por semana";">
    
    <p>Saludos,</p>
    <p><b>Equipo de control de gestión</b></p>
    """

def main():
    main_loger()
    # fecha = datetime.now().strftime('%d/%m/%Y')
    fecha = '01/08/2025'
    
    # 1. Obtener todos los dataframes
    (df_semanal_vs_ppto, df_ventas_x_sku, df_ventas_x_categoria, df_ventas_x_diasem, df_ventas_unidades_google) = obtener_dataframes(fecha)
    
    # 2. Validar que los dataframes no están vacíos
    try:
        # Validaciones de DataFrames vacíos
        validar_dataframe_no_vacio(df_semanal_vs_ppto, "DataFrame Semanal vs Presupuesto")
        validar_dataframe_no_vacio(df_ventas_x_sku, "DataFrame Ventas por SKU")
        validar_dataframe_no_vacio(df_ventas_x_categoria, "DataFrame Ventas por Categoría")
        validar_dataframe_no_vacio(df_ventas_x_diasem, "DataFrame Ventas por Día de Semana")
        validar_dataframe_no_vacio(df_ventas_unidades_google, "DataFrame Unidades Google Sheets")
        
        # Validación específica de Google Sheets (tu validador existente)
        validar_movimientos_diarios_completos(df_ventas_unidades_google, fecha=fecha, nombre_columna_fecha='Fecha')
        
        print("✅ Todas las validaciones de datos pasaron correctamente.")
        
    except DatosInvalidosError as e:
        print(f"❌ Error de validación: {e}")
        return  # Detiene el flujo si alguna validación falla
    
    # 3. Preparar tablas y comentarios
    (tabla_unidades_html, tabla_ventas_x_categoria_html, tabla_ventas_x_sku_html,
     comentario_und, total_ventas_formato, total_kg_formato, precio_prom) = preparar_tablas_y_comentarios(
        df_ventas_x_sku=df_ventas_x_sku, 
        df_ventas_x_categoria=df_ventas_x_categoria, 
        df_ventas_unidades_google=df_ventas_unidades_google, 
        fecha=fecha
    )
    
    # 4. Preparar gráficos
    grafico_ventas_comp_semanas_bas64, grafico_ventas_comp_sem_ppto_bas64 = preparar_graficos(
        df_ventas_x_diasem=df_ventas_x_diasem, 
        df_semanal_vs_ppto=df_semanal_vs_ppto
    )
    
    # 5. Construir cuerpo del email
    cuerpo_mensaje = construir_cuerpo_email(
        tabla_unidades_html=tabla_unidades_html, 
        tabla_ventas_x_categoria_html=tabla_ventas_x_categoria_html, 
        tabla_ventas_x_sku_html=tabla_ventas_x_sku_html,
        comentario_und=comentario_und, 
        total_ventas_formato=total_ventas_formato, 
        total_kg_formato=total_kg_formato, 
        precio_prom=precio_prom,
        grafico_ventas_comp_semanas_bas64=grafico_ventas_comp_semanas_bas64, 
        grafico_ventas_comp_sem_ppto_bas64=grafico_ventas_comp_sem_ppto_bas64
    )
    # 6. Enviar email
    enviar_email_con_reintentos(cuerpo_mensaje=cuerpo_mensaje,destinatarios=DESTINATARIOS,fecha_asunto=fecha,sender_email=SENDER_EMAIL,password=PASSWORD,smtp_server=SMTP_SERVER,smtp_port=SMTP_PORT)

if __name__ == "__main__":
    main()