# main.py
"""
Servidor web Flask que actúa como orquestador principal.
- Define la ruta que escucha los eventos.
- Llama a los diferentes módulos de servicio y lógica para ejecutar el proceso.
"""

import logging
from datetime import datetime
from flask import Flask, request

# Importamos los módulos que hemos creado
from notifier.logic import report_logic, graphics_logic
from notifier.services import gcs_service, email_service
from notifier.config import POWER_BI_LINK

# --- CONFIGURACIÓN DE LA APLICACIÓN ---
app = Flask(__name__)
# Es buena práctica configurar el log aquí, en el punto de entrada principal.
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# --- FUNCIÓN AUXILIAR PARA CONVERTIR DATAFRAMES A HTML ---
# Tomada de tu código original, ahora vive aquí para servir a la capa de presentación.
def df_a_html(df):
    """Convierte un DataFrame de pandas a una tabla HTML con estilos."""
    if df is None or df.empty:
        return "<p>No hay datos para mostrar en esta sección.</p>"
    
    html = '<table style="width: 100%; border-collapse: collapse; font-family: Calibri; font-size: 10pt;">'
    # Encabezados
    html += '<tr style="background-color: #003366; color: white; font-weight: bold; text-align: center;">'
    for col in df.columns:
        col_style = "padding: 8px; border: 1px solid #dddddd; text-align: center; white-space: normal;"
        html += f'<th style="{col_style}">{col}</th>'
    html += '</tr>'
    
    # Filas
    for _, row in df.iterrows():
        html += '<tr>'
        for col, value in zip(df.columns, row):
            col_style = "padding: 8px; border: 1px solid #dddddd; text-align: center;"
            if col == df.columns[0]:
                col_style += " text-align: left;"  # Primera columna alineada a la izquierda
            html += f'<td style="{col_style}">{value}</td>'
        html += '</tr>'
    
    html += '</table>'
    return html

# --- RUTA PRINCIPAL QUE ACTIVA EL PROCESO ---
@app.route("/", methods=["POST"])
def procesar_y_notificar():
    """
    Esta es la función principal que se activa por Cloud Scheduler (vía Eventarc).
    Orquesta todo el proceso de generación y envío de reportes.
    """
    logging.info("=============================================")
    logging.info("PROCESO DE NOTIFICACIÓN INICIADO POR UN EVENTO")
    logging.info("=============================================")

    try:
        # 1. Descargar todos los archivos necesarios de GCS a /tmp
        rutas_locales = gcs_service.descargar_archivos_de_gcs()

        # 2. Generar todos los DataFrames y comentarios usando la lógica de negocio
        logging.info("Generando dataframes y comentarios desde report_logic...")
        
        # Generamos los dataframes ya formateados como texto para las tablas
        df_categoria_html = df_a_html(report_logic.generar_reporte_diario_categoria_formateado(rutas_locales))
        df_producto_html = df_a_html(report_logic.generar_reporte_diario_producto_formateado(rutas_locales))
        df_und_polo, coment_und_pollos = report_logic.generar_reporte_diario_und_pollos(rutas_locales)
        df_und_polo_html = df_a_html(df_und_polo)
        # Generamos los comentarios de cumplimiento de presupuesto
        comentario_ppto_vs_real = report_logic.generar_comentario_cumplimiento_ppto(rutas_locales)

        # Generamos los comentarios para el cuerpo del correo
        ventas_total_dia, total_kg_formato, precio_prom = report_logic.generar_comentarios_producto(rutas_locales)
        
        # 3. Generar la imagen del gráfico usando la lógica de gráficos
        logging.info("Generando gráfico desde graphics_logic...")
        df_semanal_para_grafico = report_logic.generar_reporte_semanal_ventas_vs_ppto(rutas_locales)
        # La siguiente función hace todo: procesa, genera la figura y la convierte a base64
        img_base64 = graphics_logic.crear_grafico_real_vs_ppto_base64(df_semanal_para_grafico)

        # 4. Construir el cuerpo del correo en HTML con todos los datos
        logging.info("Construyendo cuerpo del correo HTML...")
        cuerpo_html = f"""
        <html>
            <body style="font-family: Calibri, sans-serif;">
                <p>Estimad@s,</p>
                <p>El día de hoy se han vendido <b>{coment_und_pollos} de pollos</b>, con un total de <b>{ventas_total_dia}</b> en ingresos (incluyendo pollos y productos adicionales) con un precio promedio <b>{precio_prom}</b> y un volumen de <b>{total_kg_formato}</b>, alcanzando un <b>{comentario_ppto_vs_real} de avance</b> en el cumplimiento del presupuesto semanal</p>
                <p>📊 Link del Dashboard: <a href="{POWER_BI_LINK}" target="_blank">Ver en Power BI</a></p>
                <p>A continuación, los reportes:</p>
                <h3>📌 Resumen de Stock (UND Pollos)</h3>
                {df_und_polo_html}
                <br>
                <h3>📌 Resumen de Ventas por Categoría</h3>
                {df_categoria_html}
                <br>
                <h3>📌 Detalle de Ventas por Producto</h3>
                {df_producto_html}
                <br>
                <h3>📌 Real vs Ppto por semana</h3>
                <img src="cid:grafico_semanal" alt="Real vs Ppto por semana">
                <br>
                <p>Saludos,</p>
                <p><b>Equipo de control de gestión</b></p>
            </body>
        </html>
        """

        # 5. Enviar el correo a través del servicio de email
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        asunto = f"Reporte Diario de Ventas Mi casero - {fecha_hoy}"
        
        email_service.enviar_reporte(asunto, cuerpo_html, img_base64)
        
        logging.info("Proceso completado exitosamente.")
        return "Proceso completado exitosamente.", 200

    except Exception as e:
        # Si algo falla en cualquier punto, lo registramos y devolvemos un error.
        logging.error(f"Ocurrió un error general en el orquestador principal: {e}", exc_info=True)
        return "Error interno en el proceso de notificación.", 500

if __name__ == '__main__':
    # Esta sección permite correr el servidor Flask localmente para pruebas.
    # No se usa en Cloud Run, que usa Gunicorn directamente.
    app.run(host='0.0.0.0', port=8080, debug=True)