import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional
import logging

# Configurar logging
logger = logging.getLogger(__name__)

def enviar_email(
    cuerpo_mensaje: str,
    destinatarios: List[str],
    fecha_asunto: str,
    sender_email: str,
    password: str,
    smtp_server: str = "smtp.office365.com",
    smtp_port: int = 587,
    subject_prefix: str = "Reporte Diario de Ventas Mi Casero"
) -> bool:
    """
    Envía un email HTML a una lista de destinatarios.
    
    Args:
        cuerpo_mensaje: Contenido HTML del email
        destinatarios: Lista de emails destinatarios
        fecha_asunto: Fecha para incluir en el asunto
        sender_email: Email del remitente
        password: Contraseña del remitente
        smtp_server: Servidor SMTP
        smtp_port: Puerto SMTP
        subject_prefix: Prefijo del asunto
    
    Returns:
        True si se envió correctamente, False si hubo error
    """
    asunto = f"{subject_prefix} - {fecha_asunto}"
    
    logger.info(f"Iniciando envío de email: '{asunto}' a {len(destinatarios)} destinatarios")
    logger.debug(f"Destinatarios: {', '.join(destinatarios)}")
    logger.debug(f"Servidor SMTP: {smtp_server}:{smtp_port}")
    
    # Validaciones básicas
    if not destinatarios:
        logger.error("Lista de destinatarios está vacía")
        return False
    
    if not cuerpo_mensaje.strip():
        logger.error("El cuerpo del mensaje está vacío")
        return False
    
    try:
        # Construir mensaje
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = ", ".join(destinatarios)
        msg["Subject"] = asunto
        msg.attach(MIMEText(cuerpo_mensaje, "html"))
        
        logger.debug("Mensaje construido correctamente")
        
        # Conectar y enviar
        logger.info(f"Conectando al servidor SMTP {smtp_server}:{smtp_port}")
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            logger.debug("Conexión SMTP establecida")
            
            # Activar TLS
            server.starttls()
            logger.debug("TLS activado")
            
            # Autenticación
            server.login(sender_email, password)
            logger.debug(f"Autenticación exitosa para {sender_email}")
            
            # Enviar email
            server.sendmail(sender_email, destinatarios, msg.as_string())
            logger.info(f"✅ Email enviado exitosamente a {len(destinatarios)} destinatarios")
            
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ Error de autenticación SMTP: {e}")
        logger.error("Verifica las credenciales del email")
        return False
        
    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"❌ Destinatarios rechazados: {e}")
        logger.error("Verifica que las direcciones de email sean válidas")
        return False
        
    except smtplib.SMTPServerDisconnected as e:
        logger.error(f"❌ Servidor SMTP desconectado: {e}")
        logger.error("Problema de conectividad con el servidor de email")
        return False
        
    except smtplib.SMTPException as e:
        logger.error(f"❌ Error SMTP general: {e}")
        return False
        
    except ConnectionError as e:
        logger.error(f"❌ Error de conexión: {e}")
        logger.error("Verifica la conectividad a internet y configuración del servidor")
        return False
        
    except Exception as e:
        logger.error(f"❌ Error inesperado al enviar email: {e}")
        logger.exception("Detalles completos del error:")
        return False

def enviar_email_con_reintentos(
    cuerpo_mensaje: str,
    destinatarios: List[str],
    fecha_asunto: str,
    sender_email: str,
    password: str,
    max_reintentos: int = 3,
    **kwargs
) -> bool:
    """
    Versión con reintentos automáticos del envío de email.
    
    Args:
        max_reintentos: Número máximo de intentos
        **kwargs: Argumentos adicionales para enviar_email
    
    Returns:
        True si se envió correctamente, False si falló después de todos los reintentos
    """
    for intento in range(1, max_reintentos + 1):
        logger.info(f"Intento {intento}/{max_reintentos} de envío de email")
        
        if enviar_email(cuerpo_mensaje, destinatarios, fecha_asunto, sender_email, password, **kwargs):
            return True
        
        if intento < max_reintentos:
            import time
            tiempo_espera = intento * 2  # Backoff exponencial simple
            logger.warning(f"Reintentando en {tiempo_espera} segundos...")
            time.sleep(tiempo_espera)
    
    logger.error(f"❌ Falló el envío después de {max_reintentos} intentos")
    return False