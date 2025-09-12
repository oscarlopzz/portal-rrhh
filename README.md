# Portal RRHH - Gestión Integral de Empleados

## 📌 Descripción General

**Portal RRHH** es una aplicación web desarrollada en **Django** que permite a las empresas centralizar y digitalizar los procesos de **Recursos Humanos (RRHH)**.

El objetivo es mejorar la eficiencia en la administración del personal, automatizar tareas rutinarias y ofrecer un espacio en línea para que los empleados gestionen sus propios trámites (vacaciones, ausencias, datos personales).

---

## 🎯 Objetivos del Sistema

- Centralizar la información del personal (datos básicos, contratos, historial).
- Simplificar la gestión de vacaciones, permisos y ausencias mediante flujos de aprobación.
- Facilitar la comunicación entre RRHH y empleados a través de notificaciones.
- Automatizar procesos como evaluaciones de desempeño y generación de reportes.

---

## 👥 Roles de Usuario

- **Administrador de RRHH**: gestión completa de empleados, solicitudes, reportes, contratos y políticas.
- **Supervisor/Jefe**: aprueba solicitudes de su equipo y accede a reportes específicos.
- **Empleado**: gestiona su perfil, solicita vacaciones/permisos y descarga documentos.

---

## 🛠️ Módulos Principales

- **Gestión de Empleados** → alta, baja, edición, contratos y documentos.
- **Asistencias, Vacaciones y Ausencias** → solicitudes y aprobaciones con registro histórico.
- **Evaluaciones de Desempeño** → formularios configurables y reportes.
- **Portal del Empleado** → panel personal con métricas y documentos.
- **Reportes y Estadísticas** → métricas globales, exportación a PDF/Excel.

---

## ⚙️ Tecnologías Utilizadas

- **Backend**: Django (Python 3.x)
- **Frontend**: Django Templates + Bootstrap/Tailwind CSS
- **Base de datos**: PostgreSQL / MySQL
- **Autenticación**: django.contrib.auth + roles
- **Notificaciones**: correos automáticos (Celery / background tasks)
- **Archivos**: FileField / ImageField

---

## 🚀 Futuras Mejoras

- Integración de nóminas.
- Chat interno con RRHH.
- APIs externas (contabilidad, ERP).
- Dashboards avanzados con gráficos interactivos.

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## Screenshots & Demo

<p align="center">
  <img src="screenshots/home.png" alt="Inicio" width="48%" />
  <img src="screenshots/mis_ausencias.png" alt="Mis ausencias" width="48%" />
</p>
<p align="center">
  <img src="screenshots/justificaciones_revisar.png" alt="Revisión de justificantes" width="48%" />
  <img src="screenshots/ausencias_revisar.png" alt="Revisión de ausencias" width="48%" />
</p>

<h3>Demo en vídeo</h3>
<p>
  <a href="videos/demo_portal_rrhh.mp4">▶ Ver demo (MP4)</a>
</p>

<!-- Si GitHub muestra el reproductor embebido en tu README: -->
<video src="videos/demo_portal_rrhh.mp4" controls width="800" preload="metadata">
  Tu navegador no soporta vídeo embebido. <a href="videos/demo_portal_rrhh.mp4">Descargar MP4</a>
</video>
