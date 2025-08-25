import io
import base64
import logging
# Configurar logging
logger = logging.getLogger(__name__)

def generar_imagen_base64(fig):
    """ Convierte el gráfico en imagen base64 """
    img_buffer = io.BytesIO()
    fig.write_image(img_buffer, format="png")
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    return img_base64 