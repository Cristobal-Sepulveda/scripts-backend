# Buscador y Notificador de Empleos - Backend (`scripts-backend`)

Este proyecto es un servicio backend basado en **FastAPI** diseñado para ejecutarse de forma programada (mediante **Google Cloud Scheduler**) o interactiva. Su objetivo principal es monitorear ofertas laborales en el portal de Empleos Públicos de Chile, filtrar aquellas correspondientes a **Kinesiología** y **Matronería** en la **Provincia de Santiago**, registrar el historial de envíos en **Google Cloud Firestore** para evitar duplicados, y notificar a los destinatarios mediante **Gmail (SMTP)**.

---

## 🛠️ Arquitectura y Diseño

El proyecto sigue principios de **Clean Architecture** (Arquitectura Hexagonal básica):
- **Capa de Dominio (`domain`)**: Contiene las entidades ([Job](file:///Users/c.sepulveda.silva/code-projects/scripts-backend/domain/entities/job.py)), excepciones personalizadas, interfaces de repositorios ([JobRepository](file:///Users/c.sepulveda.silva/code-projects/scripts-backend/domain/repositories/job_repository.py)), servicios ([EmailService](file:///Users/c.sepulveda.silva/code-projects/scripts-backend/domain/services/email_service.py)) y los casos de uso ([RunKineJobFinderUseCase](file:///Users/c.sepulveda.silva/code-projects/scripts-backend/domain/usecases/run_kine_job_finder_usecase.py), [RunMatronJobFinderUseCase](file:///Users/c.sepulveda.silva/code-projects/scripts-backend/domain/usecases/run_matron_job_finder_usecase.py), [CleanupInactiveJobsUseCase](file:///Users/c.sepulveda.silva/code-projects/scripts-backend/domain/usecases/cleanup_inactive_jobs_usecase.py)).
- **Capa de Datos (`data`)**: Implementa el acceso a Firestore ([JobRepositoryImpl](file:///Users/c.sepulveda.silva/code-projects/scripts-backend/data/repositories/job_repository_impl.py)) y el servicio de mensajería ([GmailEmailService](file:///Users/c.sepulveda.silva/code-projects/scripts-backend/data/network/gmail_email_service.py)).
- **Capa de Controladores/Presentación (`controllers`)**: Define las rutas HTTP de FastAPI ([scripts_controller](file:///Users/c.sepulveda.silva/code-projects/scripts-backend/controllers/scripts_controller.py)).
- **Capa de Infraestructura (`infrastructure`)**: Configuración global ([config.py](file:///Users/c.sepulveda.silva/code-projects/scripts-backend/infrastructure/config.py)), inyección de dependencias ([dependencies.py](file:///Users/c.sepulveda.silva/code-projects/scripts-backend/infrastructure/dependencies.py)) y middlewares de seguridad y logging ([middleware.py](file:///Users/c.sepulveda.silva/code-projects/scripts-backend/infrastructure/middleware.py)).

Los diagramas UML detallados de la arquitectura (siguiendo el modelo de vistas 4+1) se encuentran en la carpeta [uml/puml/](file:///Users/c.sepulveda.silva/code-projects/scripts-backend/uml/puml/) y sus correspondientes imágenes exportadas en [uml/images/](file:///Users/c.sepulveda.silva/code-projects/scripts-backend/uml/images/).

---

## ⚙️ Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:
- **Python 3.11** o superior.
- **Google Cloud SDK (gcloud CLI)** instalado y configurado.
- Una cuenta de **Gmail** con la configuración de **Contraseña de Aplicación** activa (necesaria para el envío SMTP).

---

## 🚀 Configuración del Entorno

### 1. Clonar y Acceder al Directorio
Navega a la carpeta del backend de scripts:
```bash
cd scripts-backend
```

### 2. Crear y Activar el Entorno Virtual (Recomendado)
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno (`.env`)
Crea un archivo `.env` en la raíz de `scripts-backend/` (si no existe) y define las credenciales de correo:
```env
EMAIL_USER="tu_correo_gmail@gmail.com"
EMAIL_PASS="tu_contrasena_de_aplicacion_gmail"
```
> [!IMPORTANT]
> `EMAIL_PASS` no es la contraseña normal de tu cuenta de Google. Debes generar una **Contraseña de Aplicación** (App Password) desde la sección de seguridad de tu cuenta de Google.

### 5. Autenticación con Google Cloud (Firestore)
Para que la aplicación pueda conectarse a Firestore de forma local, debes autenticarte en GCP utilizando Application Default Credentials (ADC):
```bash
gcloud auth application-default login
```
Alternativamente, si utilizas una cuenta de servicio local (`credentials.json`), puedes exportar la variable de entorno:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="ruta/a/tu/credentials.json"
```

---

## 🖥️ Ejecución Local

Para iniciar el servidor de desarrollo local de FastAPI:
```bash
uvicorn main:app --reload --port 8080
```

Una vez levantado, puedes acceder a:
- **API interactiva (Swagger UI)**: [http://localhost:8080/docs](http://localhost:8080/docs)
- **Verificación de estado (Root)**: [http://localhost:8080/](http://localhost:8080/)

---

## 🔗 Endpoints y Uso

La API expone los siguientes endpoints administrativos (bajo el prefijo `/scripts`):

### 1. Ejecutar Búsqueda de Kinesiología
- **Ruta**: `GET /scripts/run-job-finder/kinesiologia`
- **Descripción**: Obtiene las ofertas del portal público, filtra por la carrera de Kinesiología en la Provincia de Santiago, guarda/actualiza el contador de envíos en Firestore (máximo 2 envíos por oferta para no saturar), y envía un correo informativo a los destinatarios.

### 2. Ejecutar Búsqueda de Matronería
- **Ruta**: `GET /scripts/run-job-finder/matroneria`
- **Descripción**: Similar al endpoint anterior, pero filtra por la carrera de Matronería/Obstetricia.

### 3. Limpieza de Ofertas Inactivas
- **Ruta**: `GET /scripts/run-job-finder/cleanup`
- **Descripción**: Compara las ofertas guardadas en Firestore contra el feed activo del portal y elimina de la base de datos aquellas ofertas que ya han sido cerradas o retiradas.

---

## 🔒 Seguridad y Restricciones

Los endpoints bajo `/scripts` están protegidos por el middleware `verify_security_from_google_cloud_scheduler_task`.

- **Peticiones Locales**: Si la petición proviene de `localhost`, `127.0.0.1` o el cliente de pruebas (`testclient`), el acceso es **permitido directamente** para facilitar el desarrollo.
- **Peticiones Externas (Producción)**: El acceso está bloqueado (retornará HTTP 403 Forbidden) a menos que la petición provenga de **Google Cloud Scheduler** (identificada mediante la cabecera `X-CloudScheduler: true` o la presencia de `Google-Cloud-Scheduler` en el User-Agent).

---

## 📦 Despliegue en Google Cloud Run

Este proyecto está preparado para ejecutarse de forma segura y serverless en **Google Cloud Run**.

### 1. Compilación y Despliegue Seguro
Para compilar la imagen Docker y subirla a Cloud Run de forma segura (restringiendo el acceso público no autorizado):
```bash
gcloud run deploy job-finder-backend \
    --source . \
    --region southamerica-west1 \
    --no-allow-unauthenticated
```
> [!IMPORTANT]
> El uso de `--no-allow-unauthenticated` asegura que el servicio de Cloud Run no sea accesible de manera pública. Todas las solicitudes entrantes deberán estar debidamente autenticadas mediante tokens firmados por Google IAM.

### 2. Configuración de Tareas Programadas (Cloud Scheduler) Seguras
Para automatizar la ejecución periódica de forma segura, se configuran las tareas en Cloud Scheduler utilizando tokens de identidad OIDC:

1. **Crear una Cuenta de Servicio**: Crea una cuenta de servicio dedicada en GCP para la ejecución de la tarea.
2. **Otorgar Permisos de Invocación**: Asigna a la cuenta de servicio el rol de **Invocador de Cloud Run** (`roles/run.invoker`) sobre el servicio `job-finder-backend`.
3. **Configurar el Job de Cloud Scheduler**:
   - **Frecuencia**: Define la frecuencia cron deseada (por ejemplo, `0 * * * *` para cada 1 hora).
   - **Auth Header**: Selecciona la opción **Add OIDC token**.
   - **Service Account**: Selecciona la cuenta de servicio creada anteriormente (ej. `job-scheduler-invoker@genericstoreandroid.iam.gserviceaccount.com`).
   - **Audience**: Especifica la URL base asignada a tu servicio Cloud Run (ej. `https://job-finder-backend-496093823621.southamerica-west1.run.app`).
   - **Headers**: Opcionalmente, puedes continuar agregando la cabecera `X-CloudScheduler: true` para coincidir con la validación complementaria del middleware a nivel de aplicación.

---

## 🧪 Pruebas Automatizadas (TDD)

El proyecto incluye una suite completa de pruebas automatizadas que abarca pruebas unitarias, de integración y extremo a extremo (E2E) escritas con **pytest**.

### Ejecución de Pruebas
Para ejecutar la suite de pruebas completa dentro del entorno virtual:
```bash
.venv/bin/pytest -v
```

### Estructura de las Pruebas
Las pruebas se organizan en el directorio `tests/` de la siguiente forma:
- **Pruebas Unitarias (`tests/unit/`)**: Evalúan la lógica de negocio y las validaciones de los casos de uso (`RunKineJobFinderUseCase`, `RunMatronJobFinderUseCase` y `CleanupInactiveJobsUseCase`) utilizando mocks para aislar la base de datos y el servicio de correo.
- **Pruebas de Integración (`tests/integration/`)**: Verifican el mapeo y las llamadas a Google Cloud Firestore en `JobRepositoryImpl` simulando las respuestas de la base de datos.
- **Pruebas E2E (`tests/e2e/`)**: Prueban de extremo a extremo las llamadas HTTP a los endpoints de FastAPI (`/scripts/run-job-finder/...`) utilizando `TestClient` de FastAPI y reemplazando las dependencias externas con mocks para evitar efectos secundarios.
