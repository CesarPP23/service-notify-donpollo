# 📧 Service Notify DonPollo

Sistema completo de **automatización de notificaciones por correo** desarrollado en **Python**, con backend en **SQL Server** y frontend para gestión del servicio. Proyecto diseñado para demostrar habilidades full-stack en automatización empresarial y arquitectura de servicios.

## 🎯 Descripción del Proyecto

**Service Notify DonPollo** es una solución empresarial que automatiza el envío de correos electrónicos mediante Python, utilizando SQL Server como motor de base de datos y proporcionando una interfaz web para la gestión y monitoreo del servicio.

### Arquitectura del Sistema
- **Backend:** SQL Server (procedimientos almacenados, triggers, funciones)
- **Servicio de Automatización:** Python (lógica de negocio y envío de correos)
- **Frontend:** Interfaz web para administración y monitoreo
- **Despliegue:** SQL Server Runtime Environment

## 🛠️ Stack Tecnológico

### Backend & Base de Datos
- **SQL Server** - Motor de base de datos principal
- **T-SQL** - Procedimientos almacenados y lógica de negocio
- **SQL Server Agent** - Programación de tareas automatizadas

### Servicio de Automatización
- **Python 3.x** - Lenguaje principal para automatización
- **SMTP Libraries** - Gestión de envío de correos
- **pyodbc/SQLAlchemy** - Conectividad con SQL Server
- **Logging** - Monitoreo y trazabilidad de procesos

### Frontend & Presentación
- **HTML/CSS/JavaScript** - Interfaz de usuario
- **Framework web** - Gestión de la aplicación web
- **Responsive Design** - Adaptabilidad multiplataforma

## 📂 Estructura del Proyecto

```
service-notify-donpollo/
│
├── project/
│   └── reporte_mi_casero/          # Módulo principal del servicio
│       ├── database/               # Scripts SQL y esquemas
│       ├── email_service/          # Lógica de envío de correos
│       ├── web_interface/          # Frontend del sistema
│       └── config/                 # Configuraciones del sistema
│
├── requirements.txt                # Dependencias Python
├── .gitignore                     # Archivos excluidos del control de versiones
└── README.md                      # Documentación del proyecto
```

## ⚙️ Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- SQL Server 2019+ o SQL Server Express
- Servidor SMTP configurado

### Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/CesarPP23/service-notify-donpollo.git
   cd service-notify-donpollo
   ```

2. **Instalar dependencias Python:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar base de datos:**
   ```sql
   -- Ejecutar scripts de creación de BD en SQL Server
   -- Ubicados en project/reporte_mi_casero/database/
   ```

4. **Configurar variables de entorno:**
   ```bash
   export DB_SERVER="tu_servidor_sql"
   export DB_NAME="notify_donpollo"
   export SMTP_SERVER="tu_servidor_smtp"
   export SMTP_USER="tu_usuario"
   export SMTP_PASSWORD="tu_password"
   ```

5. **Ejecutar el servicio:**
   ```bash
   python -m project.reporte_mi_casero
   ```

## 🚀 Funcionalidades Principales

### Automatización de Correos
- ✅ Envío programado de notificaciones
- ✅ Plantillas personalizables de correo
- ✅ Gestión de listas de destinatarios
- ✅ Logs detallados de envíos

### Backend SQL Server
- ✅ Procedimientos almacenados para lógica de negocio
- ✅ Triggers para automatización de procesos
- ✅ Vistas optimizadas para reportes
- ✅ Gestión de usuarios y permisos

### Interfaz Web
- ✅ Dashboard de monitoreo en tiempo real
- ✅ Configuración de campañas de correo
- ✅ Reportes de entrega y estadísticas
- ✅ Gestión de plantillas y destinatarios

## 💼 Habilidades Técnicas Demostradas

### Desarrollo Backend
- **SQL Server Avanzado:** Diseño de esquemas, procedimientos almacenados, optimización de consultas
- **Python para Automatización:** Servicios robustos, manejo de excepciones, logging
- **Integración de Sistemas:** Conectividad Python-SQL Server, APIs de correo

### Arquitectura de Software
- **Separación de Responsabilidades:** Backend, servicio, frontend bien definidos
- **Escalabilidad:** Diseño preparado para crecimiento empresarial
- **Mantenibilidad:** Código modular y documentado

### DevOps y Despliegue
- **SQL Server Runtime:** Configuración de entornos de producción
- **Automatización:** Tareas programadas y servicios de Windows
- **Monitoreo:** Logs centralizados y alertas de sistema

## 🎯 Soft Skills Aplicadas

### Resolución de Problemas
- Análisis de requisitos empresariales complejos
- Diseño de soluciones escalables y mantenibles
- Troubleshooting de sistemas distribuidos

### Comunicación Técnica
- Documentación clara y completa del proyecto
- Código autodocumentado y comentado
- Interfaces de usuario intuitivas

### Gestión de Proyectos
- Planificación de arquitectura multicapa
- Versionado de código con Git
- Organización modular del proyecto

## 📊 Casos de Uso Empresariales

- **Notificaciones Automáticas:** Reportes diarios, alertas de sistema
- **Marketing por Email:** Campañas programadas, seguimiento de métricas
- **Comunicación Interna:** Notificaciones a equipos, recordatorios
- **Reportes Ejecutivos:** Dashboards automatizados, KPIs en tiempo real

## 🔧 Próximas Mejoras

- [ ] Integración con APIs de terceros (SendGrid, Mailgun)
- [ ] Implementación de colas de mensajes (Redis/RabbitMQ)
- [ ] Dashboard avanzado con gráficos interactivos
- [ ] Conteneurización con Docker
- [ ] CI/CD con GitHub Actions

## 🤝 Contribuciones

Este proyecto está abierto a contribuciones. Si tienes ideas para mejorarlo o encuentras algún issue, ¡no dudes en abrir un PR o issue!

---

## 👨‍💻 Sobre el Desarrollador

Este proyecto refleja mi experiencia en:
- **Desarrollo Full-Stack** con Python y SQL Server
- **Automatización de Procesos** empresariales
- **Arquitectura de Software** escalable y mantenible
- **Integración de Sistemas** heterogéneos

¿Interesado en colaborar o conocer más sobre mis proyectos? ¡Conectemos!

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/cesar-perez-palomino/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/CesarPP23)
