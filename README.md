# RPA para Reportería de Ventas y Stock 📈

Un bot de **automatización de procesos (RPA)** desarrollado en **Python**, diseñado para generar y distribuir **reportes diarios de inteligencia de negocio**, combinando datos de **SQL Server** y **Google Sheets** para una toma de decisiones ágil y basada en datos.

---

## 🎯 Visión General y Objetivo de Negocio

Este proyecto fue creado para dar soporte a la primera tienda de la empresa **"Don Pollo"**, con el objetivo de **automatizar la reportería de ventas y stock** de manera confiable, automática y eficaz.

El **reporte diario** generado por este RPA es una herramienta crucial para la dirección, permitiendo un manejo exhaustivo y cuidadoso de la operación.  
Gracias a la visibilidad proporcionada, se logró identificar una oportunidad estratégica clave: el **quiebre de stock recurrente en los SKUs principales**.  
Este hallazgo impulsó un análisis más profundo para **optimizar los niveles de inventario**, minimizando las ventas perdidas y maximizando la rentabilidad.

---

## ⚙️ Arquitectura y Flujo de Trabajo

El RPA sigue un flujo de trabajo orquestado para garantizar la **consistencia y calidad de los datos** en cada ejecución:

### 1. Extracción de Datos de Múltiples Fuentes  
- Se conecta a una **base de datos privada en SQL Server** mediante `pyodbc` para extraer datos de ventas y stock desde vistas pre-procesadas.  
- Consume información complementaria desde una **API de Google Sheets** donde se registran unidades y otros datos relevantes.

### 2. Procesamiento y Validación de Datos  
- Se implementan **validadores de datos** como un paso crítico.  
- Si la información no cumple con los criterios de calidad (datos faltantes, formatos incorrectos), el proceso se interrumpe para evitar la distribución de reportes erróneos.  
- Los datos de ambas fuentes se consolidan y procesan.

### 3. Generación de Visualizaciones  
- **Tablas HTML**: Se da formato profesional a los datos para crear tablas claras y legibles que se integran directamente en el cuerpo del correo.  
- **Gráficos dinámicos**: Barras y otros tipos de gráficos que resumen tendencias visuales.  
  Estos se codifican en **Base64** e incrustan en el email, garantizando su visualización sin necesidad de descargar adjuntos.

### 4. Composición y Envío del Reporte  
- Se ensambla un **correo HTML**, combinando tablas y gráficos.  
- El reporte es enviado automáticamente a la lista de distribución directiva a través de un servidor de correo (**Outlook**).

### 5. Despliegue  
- El servicio se ejecuta de manera programada en un **servidor privado de la compañía**.

---

## 🛠️ Stack Tecnológico

- **Lenguaje:** Python 3.x  
- **Base de Datos:** SQL Server + vistas y SPs en **T-SQL**  
- **Conectividad:** `pyodbc` (conexión nativa a SQL Server)  
- **Procesamiento de Datos:** `pandas`  
- **Visualización:** `matplotlib` / `seaborn`  
- **Integración con Google:** Google Sheets API Client  
- **Comunicación:** `smtplib` y `email` (módulos estándar de Python)  
- **Backend (fuera del repo):** Vistas T-SQL para optimización de consultas  

---

## 🛡️ Calidad de Datos y Robustez  

El sistema incorpora mecanismos para garantizar la fiabilidad:

- **Validadores de esquema:** Confirman estructura y tipos de datos esperados.  
- **Checks de nulos:** Validan que campos críticos no estén vacíos.  
- **Interrupción segura:** Ante una validación fallida se detiene el proceso y opcionalmente se notifica a un administrador.

---

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/CesarPP23/service-notify-donpollo.git
cd service-notify-donpollo
```

### 2. Crear y activar entorno virtual
```bash
python -m venv venv
# En Windows
.env\Scriptsctivate
# En macOS/Linux
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar credenciales
Crear un archivo `config.ini` o `.env` (añádelo en `.gitignore`) para credenciales seguras:  
```ini
[DATABASE]
server = tu_servidor_sql
database = tu_base_de_datos
username = tu_usuario
password = tu_contraseña

[EMAIL]
smtp_server = smtp.office365.com
port = 587
sender_email = tu_email@dominio.com
password = tu_contraseña_email

[GOOGLE_API]
credentials_path = /ruta/a/tus/credenciales.json
```

### 5. Ejecutar el RPA
```bash
python -m project.reporte_mi_casero
```

---

## 📊 Impacto en el Negocio

- Reducción de tiempos manuales en reportería.  
- Identificación de quiebres de stock y prevención de pérdidas.  
- Base sólida para crecer hacia un **data-driven business**.  

