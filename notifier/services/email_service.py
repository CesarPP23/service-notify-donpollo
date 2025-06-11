# notifier/services/email_service.py
import logging
import base64
from google.cloud import secretmanager
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from notifier.config import PROJECT_ID, SENDER_EMAIL_SECRET_ID, SENDGRID_API_KEY_SECRET_ID, RECIPIENTS

def get_secret(secret_id, version_id="latest"):
    """Obtiene un secreto de Google Cloud Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

def enviar_reporte(subject, html_content, image_base64=None):
    """
    Construye y envía el correo usando SendGrid.
    """
    logging.info("Preparando correo para enviar con SendGrid...")
    try:
        api_key = get_secret(SENDGRID_API_KEY_SECRET_ID)
        from_email = get_secret(SENDER_EMAIL_SECRET_ID)

        message = Mail(
            from_email=from_email,
            to_emails=RECIPIENTS,
            subject=subject,
            html_content=html_content
        )

        if image_base64:
            # Adjunta la imagen para que se pueda mostrar en el cuerpo del correo
            attached_image = Attachment(
                FileContent(base64.b64decode(image_base64)),
                FileName('grafico_ventas.png'),
                FileType('image/png'),
                Disposition('inline'),
                content_id='grafico_semanal' # Este ID se usa en la etiqueta <img>
            )
            message.attachment = attached_image

        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        logging.info(f"Correo enviado. Código de estado: {response.status_code}")
        return True

    except Exception as e:
        logging.error(f"CRÍTICO: Falló el envío de correo. Error: {e}")
        return False