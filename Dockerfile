# Dockerfile para el servicio Notificador

# Usamos una imagen de Python ligera y oficial.
FROM python:3.11-slim

# Establecemos el directorio de trabajo.
WORKDIR /app

# Copiamos e instalamos las librerías de Python.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el paquete de la aplicación.
COPY ./notifier ./notifier
COPY main.py .

# Exponemos el puerto y definimos el comando de arranque.
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--timeout", "1800", "main:app"]