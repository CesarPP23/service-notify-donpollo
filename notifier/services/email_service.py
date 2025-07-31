import logging
import base64
import os
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from google.cloud import secretmanager
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from notifier.config import PROJECT_ID, RECIPIENTS, SENDER_EMAIL_SECRET_ID,GET_GMAIL_CREDENTIALS_SECRET_ID

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def _get_secret(secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

def _get_gmail_credentials_from_secret(project_id, secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    secret = json.loads(response.payload.data.decode("UTF-8"))
    creds = Credentials(
        None,
        refresh_token=secret["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=secret["client_id"],
        client_secret=secret["client_secret"],
        scopes=SCOPES
    )
    if creds.expired or not creds.valid:
        creds.refresh(Request())
    return creds

def enviar_reporte(subject, html_content, image_path=None):
    """
    Construye y envía el correo usando Gmail API y OAuth2.
    Args:
        subject (str): Asunto del correo
        html_content (str): Contenido HTML del correo
        image_path (str): Ruta del archivo de imagen en /tmp (opcional)
    """
    logging.info("Preparando correo para enviar con Gmail API (OAuth2)...")
    try:
        from_email = _get_secret(SENDER_EMAIL_SECRET_ID)
        creds = _get_gmail_credentials_from_secret(PROJECT_ID, GET_GMAIL_CREDENTIALS_SECRET_ID)
        service = build('gmail', 'v1', credentials=creds)

        # Construir el mensaje MIME
        message = MIMEMultipart('related')
        message['to'] = ', '.join(RECIPIENTS)
        message['from'] = from_email
        message['subject'] = subject

        msg_alternative = MIMEMultipart('alternative')
        message.attach(msg_alternative)
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg_alternative.attach(html_part)

        if image_path and os.path.exists(image_path):
            logging.info(f"Adjuntando imagen desde: {image_path}")
            with open(image_path, 'rb') as f:
                img_data = f.read()
            image = MIMEImage(img_data)
            image.add_header('Content-ID', '<grafico_semanal>')
            image.add_header('Content-Disposition', 'inline', filename='grafico_ventas.png')
            message.attach(image)
            logging.info("Imagen adjuntada correctamente al correo")
        elif image_path:
            logging.warning(f"Ruta de imagen especificada pero archivo no encontrado: {image_path}")

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        body = {'raw': raw_message}

        result = service.users().messages().send(userId='me', body=body).execute()
        logging.info(f"Correo enviado exitosamente. Message ID: {result['id']}")
        return True

    except Exception as e:
        logging.error("CRÍTICO: Falló el envío de correo con Gmail API (OAuth2).")
        logging.error(f"Tipo de Error: {type(e)}")
        logging.error(f"Mensaje del Error: {str(e)}")
        logging.error("Traceback completo:", exc_info=True)
        return False
