# Diagrama de secuencia · Crear contrato en borrador

El dador de carga solicita la creación mediante la API. El recorrido comienza con una solicitud que cumple el esquema `ContratoCrear`.

```mermaid
sequenceDiagram
    actor D as Dador de carga
    participant R as API de contratos (contratos_router)
    participant S as ServicioContrato
    participant O as OnboardingService
    participant B as SQLite

    D->>+R: POST /contratos (datos del contrato)
    R->>+S: crear_contrato(datos_contrato)
    S->>+O: es_dador_aprobado(id_empresa_generadora)
    O->>+B: Consultar dadores_carga por user_id
    B-->>-O: Fila con estado_validacion o sin resultado
    O-->>-S: Resultado de aprobación (verdadero o falso)
    alt Dador aprobado
        S->>S: Construir ContratoModelo con ID nuevo y estado BORRADOR
        S->>+B: Insertar en contratos y confirmar la transacción
        B-->>-S: Escritura confirmada
        S-->>R: ContratoModelo creado
        R-->>D: 201 Created · contrato con ID y estado BORRADOR
    else Perfil inexistente o validación distinta de APROBADO
        S-->>R: PermissionError
        R-->>D: 403 Forbidden · detalle del rechazo
    end
    deactivate S
    deactivate R
```

## Nota de lectura

Elegimos este caso porque crear un contrato depende de una decisión que se toma en otro módulo.<br>
`ServicioContrato` delega la consulta en `OnboardingService`, que conoce el estado de validación del dador de carga.<br>
Al seguir la llamada se observa que el identificador de la empresa se usa para buscar el perfil por `user_id`.<br>
Tanto la ausencia de perfil como una validación pendiente producen el mismo rechazo antes de escribir en `contratos`.<br>
En la ruta aprobada, `ContratoModelo` asigna el identificador y el estado inicial. El cliente recibe ambos después de confirmarse la escritura.

## Referencias en el repositorio

- [Entrada HTTP y respuestas 201 y 403](../../routers/contratos_router.py)
- [Creación y persistencia del contrato](../../services/contrato_service.py)
- [Consulta del perfil y criterio de aprobación](../../services/onboarding_service.py)
- [Valores iniciales de ContratoModelo](../../domain/modelos.py) y [confirmación de la transacción](../../database/conexion.py)
