# 📧 Service Notify DonPollo

Servicio desarrollado en **Python** para el **envío automático de correos** utilizando la infraestructura de **Google Cloud**.  
Este proyecto está orientado a la automatización de notificaciones, demostrando la capacidad de integrar servicios en la nube con aplicaciones escalables y mantenibles.

## 🚀 Objetivos del proyecto
- Automatizar el **envío de notificaciones por correo**.
- Garantizar una solución **segura**, **escalable** y de **fácil mantenimiento**.
- Servir como ejemplo de integración real con **Google Cloud Services**.

## 🛠️ Tecnologías utilizadas
- **Lenguaje:** Python 3.x  
- **Cloud Provider:** Google Cloud (API de servicios de correo)  
- **Gestión de dependencias:** `requirements.txt`  
- **Buenas prácticas:** uso de `.gitignore`, modularización del proyecto, carpetas organizadas.  

## 📂 Estructura del proyecto
\`\`\`
service-notify-donpollo/
│── project/
│   └── reporte_mi_casero/    # Lógica principal del servicio
│── requirements.txt          # Dependencias del proyecto
│── .gitignore                # Archivos excluidos del versionado
\`\`\`

## ⚙️ Instalación y ejecución
1. Clonar el repositorio:
   \`\`\`bash
   git clone https://github.com/CesarPP23/service-notify-donpollo.git
   cd service-notify-donpollo
   \`\`\`
2. Instalar dependencias:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`
3. Configurar variables de entorno para credenciales de Google Cloud:
   \`\`\`bash
   export GOOGLE_APPLICATION_CREDENTIALS="tu_ruta/credenciales.json"
   \`\`\`
4. Ejecutar el servicio:
   \`\`\`bash
   python -m project.reporte_mi_casero
   \`\`\`

## 🧑‍💻 Habilidades demostradas
Este repositorio refleja mi capacidad de:
- **Desarrollo en Python** para backends y servicios de automatización.
- **Integración con Google Cloud** y manejo de credenciales seguras.
- **Organización y documentación** de proyectos técnicos.
- **Comunicación efectiva**: puedo transformar requisitos en soluciones claras y escalables.
- **Soft Skills aplicadas**: proactividad, aprendizaje continuo y capacidad de colaboración en entornos distribuidos.

## 🌟 Próximos pasos
- Integración con otros canales de notificación (SMS, WhatsApp, Push).
- Despliegue mediante contenedores Docker y Kubernetes.
- Configuración de CI/CD con GitHub Actions.

## 🤝 Contribuciones
Las contribuciones y sugerencias son bienvenidas. ¡Abramos un issue o PR y construyamos soluciones juntos!
