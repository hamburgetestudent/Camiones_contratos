# Catálogo de Requisitos Extrafuncionales (REF)
**Proyecto:** Plataforma de Centralización y Digitalización de Contratos de Transporte Terrestre de Carga (Camiones y Motor de Subastas)  
**Documento:** `RF.md` / `ReqExtrafuncionales.md`

---

## 1. Introducción

El presente documento define el catálogo de **Requisitos Extrafuncionales (REF)** para la plataforma de contratos de transporte de carga y subastas de fletes. Estos requisitos representan los atributos de calidad, restricciones técnicas, limitaciones de proyecto y consideraciones operativas que condicionan la arquitectura del software.

---

## 2. Catálogo General de Requisitos Extrafuncionales

A continuación se presenta la matriz consolidada y priorizada de los requisitos extrafuncionales del sistema:

| ID | Tipo / Categoría | Descripción | Criterio / Métrica de Aceptación | Prioridad |
| :--- | :--- | :--- | :--- | :--- |
| **REF-01** | Calidad de servicio (Perf.) | El sistema debe responder en menos de 2 segundos. | Tiempo de respuesta del backend (latencia de API) $\le 2.0\text{ s}$ en el percentil 95 ($P_{95}$) para consultas, creación de contratos y ofertas bajo carga típica. | **Alta** |
| *REF-02* |  Restricción técnica. | El sistema debe exponer y consumir la información geográfica y de telemetría mediante una interfaz RESTful estructurada bajo estándares abiertos de geolocalización. | Los mensajes entrantes y salientes deben validar su esquema contra modelos Pydantic antes de ser procesados. Compatible con la especificación de objetos GeoJSON para su consumo directo en clientes web/desktop. | *Media* |
| **REF-03** | Calidad de servicio (Seg.) | Autenticación y autorización requerida para todas las operaciones clave. | Acceso protegido mediante tokens Bearer/JWT y autorización basada en roles (RBAC: Generador, Transportista, Admin). Ningún contrato u oferta puede crearse de forma anónima. | **Alta** |
| **REF-04** | Calidad de servicio (Consistencia y Concurrencia) | Integridad transaccional y prevención de condiciones de carrera en subastas y contratos. | La máquina de estados no debe permitir transiciones inválidas ni adjudicaciones dobles frente a postulaciones concurrentes de múltiples transportistas. | **Alta** |
| **REF-05** | Restricción técnica | Compatibilidad con aplicaciones de escritorio (Electron) y navegadores web modernos (SPA). | La interfaz cliente debe ejecutarse de manera fluida en Electron y ser integrable como Single Page Application (SPA) compatible con Chromium, Firefox y Edge. | **Media** |
| **REF-06** | Restricción técnica | Intercambio de información mediante API RESTful estandarizada sobre JSON. | Comunicación cliente-servidor estrictamente bajo protocolo HTTP/HTTPS utilizando JSON con esquemas de validación unificados en Pydantic. | **Media** |
| **REF-07** | Restricción técnica | Backend desacoplado en Python y framework FastAPI. | Servidor backend construido sobre Python 3.12+ (compatible con 3.14), framework FastAPI y servidor ASGI Uvicorn para alta eficiencia asíncrona. | **Media** |
| **REF-08** | Restricción de proyecto | implementacion del sistema como equipo | El alcance debe implementarse de forma iterativa e incremental mediante control de versiones en GitHub. | **Media** |
| **REF-09** | Restricción de proyecto | Licenciamiento de dependencias de código abierto (Open Source). | El stack de dependencias (FastAPI, Electron, TypeScript, Pydantic) debe contar con licencias permisivas (MIT, Apache 2.0, ISC) sin costo por licencia. | **Baja** |
| **REF-10** | Otros no funcionales (Usabilidad e Idioma) | Interfaz de usuario en español y adaptada a la logística nacional. | Interfaz gráfica y mensajes de retroalimentación 100% en idioma español, manejando moneda en pesos chilenos (CLP), IVA y normativas de carga (códigos ONU). | **Baja** |
| **REF-11** | Otros no funcionales (Mantenibilidad) | Arquitectura modular desacoplada en capas (Routers, Services, Domain, DAO). | La capa de almacenamiento en memoria debe poder ser reemplazada por una base de datos relacional (PostgreSQL/SQLite) sin alterar la lógica de negocio ni los controladores. | **Media** |
| **REF-12** | Otros no funcionales (Auditoría y Trazabilidad) | Registro y trazabilidad de eventos del ciclo de vida del contrato. | Toda creación, actualización de estado, postulación y adjudicación debe registrar marca de tiempo UTC y el identificador de usuario asociado. | **Media** |
| **REF-13** | Usabilidad| Arquitectura de interfaz oara el usuario intuitiva.| La interfaz debe permitir que al menos el 80% de los usuarios de prueba realice las funciones principales sin asistencia y en un máximo de tres pasos por operación. | **Alta** |


---

## 3. Clasificación Detallada por Categoría

### 3.1 Calidad de Servicio
* **REF-01 (Rendimiento / Performance):** La interacción entre el transportista/generador y el sistema debe ser ágil, especialmente en la visualización de contratos activos y envío de ofertas en subastas.
* **REF-03 (Seguridad):** La confidencialidad y validez legal de las cotizaciones y contratos exige la identificación inequívoca del emisor y validación de permisos por rol.
* **REF-04 (Consistencia y Concurrencia):** Garantiza que una oferta o cierre de contrato sea atómico y coherente frente a peticiones simultáneas.

### 3.2 Restricciones Técnicas
* **REF-02 (Estándar de Datos y Telemetría):** Exposición y consumo de geolocalización e información telemática estructurada bajo el estándar abierto GeoJSON y esquemas Pydantic.
* **REF-05 (Cliente Multiplataforma / SPA):** Permite a los usuarios operar desde equipos de escritorio mediante Electron (TypeScript/HTML5/CSS3) o navegadores web modernos.
* **REF-06 (Formato de Datos):** Estandarización de contratos y ofertas mediante esquemas JSON tipados y validados.
* **REF-07 (Tecnología Backend):** Empleo de Python con FastAPI y Uvicorn para maximizar rendimiento mediante concurrencia asíncrona.

### 3.3 Restricciones de Proyecto
* **REF-08 (sistema y equipo): Piorización de funcionalidades mínimas viables (MVP),arquitectura limpia Y tipos de modelo de forma iterativa.
* **REF-09 (Costos y Licenciamiento):** Empleo exclusivo de herramientas sin costos de licenciamiento corporativo.

### 3.4 Otros Requisitos No Funcionales
* **REF-10 (Usabilidad y Localización):** Experiencia de usuario contextualizada a transportistas y empresas de carga en Chile (pesos chilenos CLP, cálculo de IVA, nomenclatura UN para cargas peligrosas).
* **REF-11 (Mantenibilidad y Extensibilidad):** Desacoplamiento estricto para facilitar pruebas unitarias (`tests/`) y transición desde almacenamiento en memoria hacia persistencia persistente (SQL/NoSQL).
* **REF-12 (Trazabilidad y Auditoría):** Registro cronológico inmutable de postulaciones, adjudicaciones y cambios de estado.
* **REF-13 (Usabilidad):** La interfaz debe ser intuitiva, clara y fácil de utilizar, permitiendo que los usuarios realicen las operaciones principales de camiones, contratos y ofertas sin asistencia.

---

## 4. Decisiones de Diseño Arquitectónico para los REF de Prioridad Alta

En concordancia con los lineamientos del proyecto, los requisitos de **prioridad Alta** son abordados explícitamente en el diseño arquitectónico:

### 4.1 Abordaje de REF-01 (Rendimiento: Respuesta < 2s)
1. **Framework Asíncrono ASGI:** Adopción de **FastAPI** ejecutándose sobre el servidor ASGI **Uvicorn**, lo que permite manejar múltiples solicitudes I/O sin bloquear el hilo de ejecución principal.
2. **Serialización y Validación de Alto Rendimiento:** Uso de **Pydantic v2** (compilado en Rust a través de `pydantic-core`), reduciendo significativamente los tiempos de serialización y deserialización de contratos complejos y listas de postulaciones.
3. **Persistencia Optimizada y Desacoplada (Capa DAO):** La capa de acceso a datos (`dao/`) implementa accesos indexados en memoria por ID y filtros en memoria optimizados, asegurando tiempos de respuesta en el orden de milisegundos ($< 50\text{ ms}$ a nivel de servidor).


### 4.2 Abordaje de REF-02 (Seguridad: Autenticación y Autorización Estricta)
1. **Esquema de Autenticación Centralizado:** Módulo `routers/auth_router.py` y `services/usuario_service.py` con emisión y validación de credenciales bajo estándar `Bearer Token`.
2. **Control de Acceso Basado en Roles (RBAC):** Modelo de dominio (`domain/modelos_usuario.py`) con roles explícitos (`GENERADOR`, `TRANSPORTISTA`, `EMPRESA`, `INDEPENDIENTE`, `ADMIN`), donde cada endpoint valida los privilegios del usuario antes de ejecutar la acción solicitada.
3. **Almacenamiento Seguro de Credenciales:** Encriptación y hashing de contraseñas (`password_hash`), evitando la persistencia de claves en texto plano.

### 4.3 Abordaje de REF-03 (Consistencia y Concurrencia en Subastas y Contratos)
1. **Máquina de Estados Finita Determinista:** La clase `MaquinaEstadosContrato` y `EstadoContrato` en `domain/maquina_estados.py` valida rigurosamente cada transición permitida (por ejemplo: `BORRADOR -> PUBLICADO -> EN_SUBASTA -> ADJUDICADO -> EN_TRANSITO -> FINALIZADO`), rechazando cambios de estado ilegales.
2. **Capa de Servicios como Frontera Transaccional:** La lógica de postulaciones (`services/subasta_service.py` y `domain/postulacion.py`) centraliza las reglas de adjudicación para garantizar que la selección de un transportista ganador sea atómica y coherente.

### 4.4 Abordaje de REF-13 (Usabilidad: Interfaz intuitiva)

1. **Capa de presentación centrada en las tareas:** La interfaz desarrollada en Electron y TypeScript se organizará de acuerdo con las principales acciones del sistema, como iniciar sesión, consultar contratos, publicar servicios y enviar ofertas.
2. **Navegación simple y consistente:** Todas las pantallas utilizarán una estructura visual uniforme, con menús, botones, colores y nombres consistentes. Las opciones se mostrarán según el rol del usuario, evitando presentar funciones que no le correspondan.
3. **Reducción de pasos:** Los flujos principales del sistema se diseñarán para que puedan realizarse en un máximo de tres pasos, evitando formularios innecesarios y navegaciones confusas.
4. **Mensajes claros para el usuario:** La interfaz mostrará mensajes en español para confirmar acciones, informar errores, indicar campos obligatorios y comunicar problemas de conexión. No se mostrarán mensajes técnicos difíciles de comprender.
5. **Validación y prevención de errores:** Los formularios validarán los campos obligatorios y los formatos incorrectos antes de enviar la información al backend. En caso de error, se indicará claramente qué dato debe corregirse.
6. **Evaluación de usabilidad:** La solución será evaluada mediante una prueba con usuarios. Se considerará cumplido el requisito cuando al menos el 80% de los usuarios pueda realizar las funciones principales sin asistencia y en un máximo de tres pasos por operación.

