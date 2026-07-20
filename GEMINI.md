# Manifiesto y Directivas de Arquitectura de Software (GEMINI.md)

Este documento establece los cimientos de pensamiento de diseño y las reglas mandatorias que gobiernan el desarrollo y la evolución de este repositorio. Sirve como directiva permanente para cualquier desarrollador humano o asistente de Inteligencia Artificial (IA) que colabore en este proyecto.

---

## 📖 Contexto del Proyecto

Toda decisión de diseño, modelamiento y arquitectura en este repositorio se rige y evalúa bajo los estándares de la siguiente evaluación formal:
*   **Rúbrica y Requisitos:** [Examen de Arquitectura (PDF)](backend/docs/examen_arquitectura.pdf)

Este repositorio contiene dos proyectos que deben modelarse por separado bajo estándares formales de arquitectura de software:
1.  **Buscador y Notificador de Empleos (`scripts-backend`):** Sistema backend FastAPI desplegado en GCP para monitorear y alertar ofertas laborales.
2.  **Tienda Genérica y App Móvil (`GenericStoreAndroid`):** Aplicación móvil Android conectada a un backend FastAPI desarrollado bajo arquitectura hexagonal.

---

## 🎯 Filosofía del Diseño Arquitectónico

En este repositorio, **el código y su documentación arquitectónica son una sola entidad**. Una lógica de negocios que funcione pero no esté debidamente modelada y evaluada bajo estándares formales de arquitectura de software se considera **incompleta**.

Como arquitectos de software, nuestro pensar debe sustentarse en tres pilares fundamentales:
1.  **Visualización Multidimensional:** Todo componente de los sistemas debe ser observable desde las vistas lógica, de procesos, de despliegue y física (según las 4+1 vistas de Kruchten).
2.  **Mitigación Científica del Riesgo:** Las decisiones de diseño no son aleatorias; se evalúan en base a atributos de calidad (Rendimiento, Escalabilidad, Seguridad) utilizando metodologías formales como **ATAM**.
3.  **Trazabilidad:** Cualquier cambio en la lógica de negocios debe reflejar inmediatamente su impacto en el modelo entidad-relación (MER) y en el árbol de utilidad del sistema.

---

## 🚧 Regla de Oro: Garantía de Documentación Activa

Los artefactos y diagramas arquitectónicos dentro de la carpeta `/uml` **solo se actualizarán cuando el usuario lo solicite de manera explícita**. No se realizarán actualizaciones automáticas de los archivos PlantUML (`.puml`) ni imágenes tras modificaciones de código, a menos que haya una petición directa del usuario.

*   Para el Buscador de Empleos: Guardar en `/uml/scripts-backend/puml/` (con prefijo `scripts_backend_`)
*   Para el Almacén y App Móvil: Guardar en `/uml/GenericStoreAndroid/puml/` (con prefijo `generic_store_android_`)

### Artefactos Requeridos por Carpeta:

#### 1. La Vista Lógica (Estructura y Comportamiento)
*   **Diagrama de Clases (`scripts_backend_class_diagram.puml` / `generic_store_android_class_diagram.puml`):** Actualizar las firmas de métodos, tipos de retorno, atributos y relaciones de dependencia/asociación de las clases y capas del proyecto.
*   **Diagrama de Secuencia (`scripts_backend_sequence_diagram.puml` / `generic_store_android_sequence_diagram.puml`):** Ilustrar paso a paso el ciclo de vida de los flujos de negocio e interacciones de red.
*   **Diagrama de Comunicación (`scripts_backend_communication_diagram.puml` / `generic_store_android_communication_diagram.puml`):** Mostrar el paso de mensajes y colaboración entre los objetos internos del sistema.

#### 2. La Vista de Procesos (Flujo de Ejecución)
*   **Diagrama de Actividad (`scripts_backend_activity_diagram.puml` / `generic_store_android_activity_diagram.puml`):** Modelar las bifurcaciones lógicas, validaciones de seguridad/middleware y flujos excepcionales de los controladores.

#### 3. La Vista de Despliegue y Física (Entorno de Ejecución)
*   **Diagrama de Componentes (`scripts_backend_component_diagram.puml` / `generic_store_android_component_diagram.puml`):** Modelar la estructura física y lógica de los paquetes y módulos del sistema.
*   **Diagrama de Paquetes (`scripts_backend_package_diagram.puml` / `generic_store_android_package_diagram.puml`):** Definir cómo se organiza la jerarquía de directorios en el backend.
*   **Diagrama de Despliegue Físico (`scripts_backend_deployment_diagram.puml` / `generic_store_android_deployment_diagram.puml`):** Ilustrar el despliegue de los servicios (GCP, APIs externas, o dispositivos físicos y emuladores móviles).

#### 4. Casos de Uso
*   **Diagrama de Casos de Uso (`scripts_backend_use_cases.puml` / `generic_store_android_use_cases.puml`):** Documentar exactamente **1 diagrama de caso de uso genérico** del sistema y **2 diagramas detallados** con sus flujos principales y alternativos.

#### 5. Persistencia y MER
*   **Modelo Entidad-Relación (MER):** Detallar la persistencia o estructuras de datos utilizadas (Firestore, bases de datos o colecciones en memoria), indicando la estrategia de almacenamiento, indexación o particionamiento.
*   **Propuesta de Objetos:** Definir las clases u objetos de dominio de software que interactúan directamente con la capa de datos.

#### 6. Evaluación y Mitigación bajo ATAM
*   **Log de Riesgos:** Mantener y actualizar un registro de exactamente **5 riesgos clave de la arquitectura**, evaluando su Probabilidad (P), Impacto (I) y su respectiva Mitigación.
*   **Evaluación ATAM:** Mantener el Árbol de Utilidad del sistema identificando escenarios priorizados en base a los atributos de calidad (Seguridad, Escalabilidad, Disponibilidad, Mantenibilidad).

---

## 🛠️ Estándar Técnico de Entregables (No Markdown para Consumo Propio)

La documentación se genera con un propósito de presentación académica y profesional. Por lo tanto:
*   **Código PlantUML (`.puml`):** Todos los diagramas UML deben ser generados en la subcarpeta `puml/` de cada carpeta.
*   **Imágenes Renderizadas (`/images/*.png`):** Cada carpeta de UML debe contener una subcarpeta `images/` con las imágenes PNG compiladas correspondientes a cada diagrama `.puml` para permitir su visualización directa en el workspace.
*   **Tablas de Riesgo y ATAM:** Formatear los análisis de riesgo y árboles de utilidad en tablas Markdown limpias en el archivo `architecture.md` (o archivo correspondiente) para permitir al usuario copiarlos directamente a Word o PowerPoint.

## Estandar del código.
No comentaras mi código.

## Despliegue.
El despliegue a Google Cloud Run se hará únicamente cuando el usuario lo solicite de manera explícita. No se realizará de forma automática tras cambios de código.

## 📝 Formato de Respuesta Obligatorio
Al finalizar cada turno (sea de avance intermedio o de cierre final), debes estructurar obligatoriamente tu respuesta siguiendo este orden:
1. **Resumen Técnico:** Detalle de los cambios por capa (Domain, Data, Presentation, UI, Infrastructure, etc.).
2. **Estructura Visual:** Representar el árbol de archivos (árbol de directorios modificado) indicando claramente qué archivos son `(Nuevo)` y cuáles `(Modificado)` o eliminados.
3. **Reporte y Condiciones de Cierre:** Detalle del éxito o fracaso de las pruebas unitarias, sintaxis, compilación o scripts de verificación.

## Consideraciones: Elaboración de Tests
1) Todos mis test deben seguir la lógica de Arrange, Act, Assert.