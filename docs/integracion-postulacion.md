# Integración y verificación de la postulación a una carga

Un dador publica una carga y un transportista habilitado envía una oferta desde el panel. La operación termina cuando el dador puede consultar la oferta y el contrato pasa de `PUBLICADO` a `EN_POSTULACION`. La [prueba del panel](../frontend/tests/panel.e2e.cjs) usa las mismas páginas que carga Electron y contrasta el mensaje en pantalla con dos lecturas posteriores de la API.

## Recorrido de los datos

```mermaid
sequenceDiagram
    actor D as Dador
    actor T as Transportista
    participant P as Panel de transportista
    participant A as FastAPI y routers
    participant S as ServicioSubasta y dominio
    participant B as SQLite
    D->>A: Login, crear contrato y publicar por ID
    A->>B: Guardar contrato y estado PUBLICADO
    T->>P: Iniciar sesión y abrir Subastas y Cargas
    P->>A: Token de sesión, consulta de cargas y estado KYC
    A-->>P: Cargas disponibles y habilitación del transportista
    T->>P: Elegir carga e ingresar tarifa y horas
    alt Tarifa inferior a 5000 CLP en el panel
        P-->>T: El formulario indica el mínimo y bloquea el envío
    else Formulario válido
        P->>A: POST /subastas/postular con token, aprobación KYC y oferta JSON
        A->>S: PostulacionCrear con IDs, precio, horas y comentario
        S->>B: Abrir transacción y buscar contrato por ID
        alt Carga disponible y plazo vigente
            S->>B: Insertar POSTULADA y actualizar contrato en una transacción
            A-->>P: 201 con oferta, ID y estado
            P-->>T: Postulación enviada correctamente
            D->>A: Consultar contrato y sus postulaciones
            A-->>D: EN_POSTULACION y oferta registrada
        else Carga inexistente
            S-->>A: Error de dominio y reversión de la transacción
            A-->>P: 404 con detalle que identifica la carga
        end
    end
```

El [panel](../frontend/codigos/paginas/panel/transportista.js) obtiene el estado de onboarding y envía el indicador de aprobación en la consulta. FastAPI comprueba la sesión y Pydantic valida el cuerpo antes de llamar al [router](../routers/subasta_router.py). El [servicio](../services/subasta_service.py) comprueba la disponibilidad y el plazo. La [conexión SQLite](../database/conexion.py) confirma o revierte las escrituras juntas. El [adaptador de errores](../routers/comun.py) convierte una carga inexistente en HTTP 404. El panel muestra el detalle recibido si falla el envío.

## Registro de ejecución

Entorno local compartido por los tres casos el 24 de noviembre de 2026: Windows, Python 3.15.2, FastAPI 0.162.4, Pydantic 2.14.3, Uvicorn 0.54.0, SQLite 3.53.4, Node 26.13.0, Playwright 1.65.1 y Edge 158.0.4370.33. La prueba inicia la API en un puerto local libre, configura `SQLITE_DB_PATH` en un directorio temporal con permiso de escritura e inicializa el esquema y los usuarios ficticios. Usa el navegador y el servidor reales. La ventana nativa de Electron queda fuera de esta comprobación.

| Caso y pasos | Resultado esperado | Resultado obtenido |
| --- | --- | --- |
| **Datos inválidos.** Publicar la carga Valparaíso–Concepción, abrirla como transportista e intentar enviar 4.900 CLP. Consultar contrato y ofertas como dador. | El formulario exige al menos 5.000 CLP. El contrato conserva todos sus campos y sigue sin ofertas. | El navegador activó `rangeUnderflow`. La consulta devolvió el contrato idéntico al inicial, en `PUBLICADO`, y una lista vacía. |
| **Datos válidos.** En el mismo formulario, corregir a 180.000 CLP y enviar. Leer el contrato y la lista de ofertas desde la sesión del dador. | HTTP 201, confirmación visible, una oferta por el importe indicado y transición a `EN_POSTULACION`. | El panel confirmó el envío. La API devolvió `POSTULADA` para el ID de la carga. La lectura posterior devolvió exactamente esa oferta y el contrato en `EN_POSTULACION`. |
| **Recurso ausente.** Repetir por HTTP la solicitud del transportista con la misma sesión y datos, sustituyendo solo el ID de carga por un UUID inexistente. Consultar de nuevo la carga de control y sus ofertas. | HTTP 404 con indicación de carga inexistente. La oferta anterior y su contrato se conservan. | La API respondió 404 con el detalle «no existe». El contrato coincidió campo por campo con el anterior y la lista conservó su única oferta. |

El último caso reproduce una referencia caducada en la conexión panel–API. Se envía directamente porque el selector del panel solo ofrece cargas existentes. Ningún servicio externo fue simulado.

## Cómo repetir la demostración

Desde la raíz, con Python, Node y Microsoft Edge instalados, ejecutar en PowerShell:

```powershell
python -m pip install -r requirements.txt pytest httpx
npm --prefix frontend ci
npm --prefix frontend run test:panel
python -m coverage run -m pytest -q
python -m coverage report -m
python -m coverage xml
```

El panel imprime un resultado por caso y termina con código 0 si se cumplen todas las aserciones. La suite local registró **216 pruebas y 70 subpruebas aprobadas**. Coverage.py 7.17.2 midió **93,9 %** en las capas Python configuradas, con 1.240 sentencias y 232 ramas. [Reporte local por módulo](cobertura-criterio-6.txt).

La [ejecución del commit de entrega `c091544`](https://github.com/hamburgetestudent/Camiones_contratos/actions/runs/45510972035) ejecuta la suite con cobertura en el trabajo de backend y los tres casos en el trabajo de frontend. El artefacto `cobertura` contiene el XML de esa ejecución.
