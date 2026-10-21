# Tabla de verificación – Creación de contratos

**Asignatura:** Taller de Programación Avanzada ISF224  
**Unidad:** 2.2 – Construcción para la verificación  
**Proyecto:** Camiones_contratos  
**Funcionalidad seleccionada:** Creación de contratos  

## Ficha de operación: Creación de contratos

Esta ficha documenta las precondiciones, postcondiciones, invariantes, validaciones defensivas y dependencias explícitas de la funcionalidad seleccionada.

| Elemento | Registro del equipo |
|---|---|
| **Funcionalidad y operación** | **Creación de contrato:** `ServicioContrato.crear_contrato(datos: ContratoCrear) -> ContratoModelo`.<br><br>**Ruta HTTP:** `POST /contratos`.<br><br>**Archivos relacionados:**<br>• `services/contrato_service.py`<br>• `domain/modelos.py`<br>• `dao/contrato_dao.py`<br>• `routers/contratos_router.py` |
| **Propósito** | Crear un contrato nuevo en estado `BORRADOR` con sus especificaciones de carga, ruta y condiciones comerciales, validando las reglas de negocio (fechas, capacidades, coherencia financiera e IVA) y la verificación KYC de la empresa generadora, persistiendo la entidad vía DAO y devolviendo el contrato creado. |
| **Precondiciones** | **1.** El payload de entrada cumple con las validaciones de esquema y negocio de `ContratoCrear`: fechas en orden cronológico con anticipación mínima de salida, origen y destino distintos, peso total menor o igual a la capacidad del camión, requerimientos según tipo de carga (código ONU para carga peligrosa, embalaje mínimo para frágil, termo para refrigerada/perecedera, blindaje para valores) y coherencia en montos (Neto + IVA = Total, con IVA 19% en CLP).<br><br>**2.** La empresa generadora (`id_empresa_generadora`) existe y cuenta con su verificación KYC/Onboarding en estado APROBADO en el `OnboardingService`, y el repositorio `ContratoDAO` está disponible. |
| **Postcondiciones** | **1.** Se persiste un `ContratoModelo` en estado `BORRADOR` con su UUID asignado, conservando todos los datos de ruta, carga y financieros ingresados.<br><br>**2.** La operación devuelve el `ContratoModelo` creado y la ruta responde con **HTTP 201 Created** con la representación completa del contrato. |
| **Invariante** | La identidad de la empresa generadora y los datos del contrato permanecen íntegros e inmutables durante la creación; el estado inicial es invariablemente `BORRADOR`; una solicitud con KYC no aprobado o con datos inválidos no persiste ni crea ningún contrato en el sistema. |
| **Validación defensiva** | **Entrada válida:** datos de contrato coherentes (origen "SANTIAGO", destino "VALPARAISO", carga GENERAL, peso 15.000 KG en camión de 20.000 KG, fechas válidas, neto $100.000, IVA $19.000 y total $119.000 CLP) con empresa generadora aprobada por KYC.<br>**Respuesta esperada:** contrato creado en estado `BORRADOR`, UUID asignado y **HTTP 201**.<br><br>**Entrada inválida 1:** empresa generadora sin verificación KYC o con estado no aprobado.<br>**Respuesta esperada:** `PermissionError` en el servicio y respuesta **HTTP 403**, "...no cuenta con su verificacion KYC/Onboarding en estado APROBADO", sin guardar.<br><br>**Entrada inválida 2:** datos de contrato inconsistentes (ej. monto IVA no corresponde al 19% del neto en CLP, peso excede capacidad, o código ONU ausente en carga peligrosa).<br>**Respuesta esperada:** `ValueError` / `ValidationError` de Pydantic y respuesta **HTTP 400** (o **HTTP 422** en payload malformado), sin guardar. |
| **Dependencia explícita** | `ContratoDAO`, inyectado en el constructor (`dao: ContratoDAO`) para abstraer la persistencia.<br><br>`OnboardingService`, inyectado en el constructor (`onboarding_service: OnboardingService \| None = None`) con fallback a instancia global, permitiendo mockear en pruebas la verificación KYC. |
| **Evidencia de ejecución** | **Archivo de pruebas:** `tests/test_contrato_service.py` (o pruebas integradas en `services/contrato_service.py`).<br><br>**Comando:**<br>`python -m pytest tests/ -v` o `python services/contrato_service.py`<br><br>**Evidencias que deben adjuntarse:**<br>• Captura del caso exitoso **HTTP 201**.<br>• Captura del rechazo por KYC no aprobado **HTTP 403**.<br>• Captura del rechazo por datos inconsistentes **HTTP 400** / **HTTP 422**.<br>• Salida real de las pruebas ejecutadas con `pytest` o `unittest`. |

## Evidencias pendientes de adjuntar

- [ ] Captura de la creación exitosa con HTTP 201.
- [ ] Captura del intento de creación con empresa no aprobada (KYC), HTTP 403.
- [ ] Captura de entrada inválida o inconsistente, HTTP 400 / HTTP 422.
- [ ] Resultado de la ejecución de `pytest` o `unittest`.
- [ ] Confirmación de que las validaciones y la dependencia explícita funcionan en el código del proyecto.

**Nota:** Las respuestas descritas en la tabla representan los resultados esperados según la ficha de operación. Las evidencias deben incorporarse después de ejecutar y comprobar los casos correspondientes.
