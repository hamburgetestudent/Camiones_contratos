# CR-203: Auditoría y reconstrucción histórica

**Issue:** [#49](https://github.com/hamburgetestudent/Camiones_contratos/issues/49)  
**Responsable:** Cristián Benjamín Palma Cataldo  
**Prioridad:** Alta  
**Fecha de análisis:** 12 de septiembre de 2026

## 1. Solicitud de cambio

Como organismo fiscalizador, quiero reconstruir el estado exacto de un contrato de
transporte en una fecha determinada, para conocer qué bases regían, qué ofertas
existían, quién las revisó y qué información se utilizó al tomar una decisión.

Una corrección posterior no puede modificar ni borrar el hecho original. Debe
incorporarse como un nuevo evento, indicando quién la realizó, cuándo, por qué y
qué registro corrige.

## 2. Análisis de impacto

| Componente | Impacto | Cambio requerido |
| --- | --- | --- |
| Dominio | Alto | Modelar eventos, actuaciones, correcciones y vistas históricas. |
| Persistencia | Alto | Incorporar un ledger SQLite append-only con bloqueo de `UPDATE` y `DELETE`. |
| Servicios | Alto | Auditar creación y cambios de contrato, ofertas, revisión y adjudicación. |
| API REST | Medio | Exponer historial, reconstrucción, correcciones e integridad. |
| Seguridad | Medio | Identificar al responsable mediante `X-User-Id`; no registrar credenciales. |
| Pruebas | Alto | Verificar inmutabilidad, cortes temporales, correcciones y cadena de hashes. |
| Frontend | Bajo | No se modifica en este cambio; podrá consumir los endpoints posteriormente. |

El cambio amplía **REF-12 (Auditoría y Trazabilidad)** y lo eleva a prioridad alta.
No altera los modelos públicos actuales de contratos u ofertas.

## 3. Decisión de diseño

Se adopta un registro de eventos inmutable, separado de los DAOs operacionales:

1. Cada actuación genera una instantánea JSON con actor y fecha UTC.
2. Los eventos se anexan a SQLite y nunca se actualizan ni eliminan.
3. Cada evento contiene el hash SHA-256 del anterior para el mismo transporte.
4. La reconstrucción aplica los eventos cuya fecha sea menor o igual al corte.
5. Una corrección es un evento nuevo que referencia el UUID del evento original.

SQLite se utiliza como adaptador local persistente del MVP. La separación
`Router -> Service -> DAO` permite sustituirlo por PostgreSQL sin cambiar las
reglas de reconstrucción.

## 4. Información registrada

Cada evento conserva:

- UUID y secuencia de anexado;
- contrato o transporte afectado;
- entidad y acción ejecutada;
- UUID del actor responsable;
- fecha y hora UTC;
- instantánea completa posterior a la actuación;
- reglas de negocio vigentes;
- antecedentes considerados en revisiones o decisiones;
- referencia y motivo cuando se trata de una corrección;
- hash anterior y hash propio.

No se incluyen contraseñas, tokens ni secretos.

## 5. Criterios de aceptación

- **CA1:** Toda creación o cambio de estado de contrato queda registrado con actor,
  fecha UTC, instantánea y bases aplicadas.
- **CA2:** Toda oferta queda registrada al crearse y cuando cambia de estado.
- **CA3:** Una adjudicación conserva el revisor, todas las ofertas consideradas y
  la oferta ganadora.
- **CA4:** `GET /auditoria/transportes/{id}/reconstruccion?hasta=...` devuelve el
  contrato, las ofertas, revisiones, decisiones y bases existentes en ese instante.
- **CA5:** Una corrección crea un evento enlazado; el original sigue disponible y
  una reconstrucción anterior a la corrección no cambia.
- **CA6:** SQLite rechaza físicamente operaciones `UPDATE` y `DELETE` en el ledger.
- **CA7:** La verificación de integridad detecta cualquier ruptura de la cadena
  SHA-256.
- **CA8:** Los registros se conservan sin purga automática, permitiendo una política
  de retención mínima de dos años.
- **CA9:** Las pruebas automatizadas cubren flujo completo, corrección e
  inmutabilidad.

## 6. Endpoints incorporados

| Método | Ruta | Resultado |
| --- | --- | --- |
| `GET` | `/auditoria/transportes/{id}/eventos` | Evidencia cronológica completa. |
| `GET` | `/auditoria/transportes/{id}/reconstruccion?hasta=...` | Estado a la fecha de corte. |
| `POST` | `/auditoria/correcciones` | Nueva corrección; exige `X-User-Id`. |
| `GET` | `/auditoria/integridad` | Validación de la cadena de hashes. |

## 7. Riesgos y mitigaciones

| Riesgo | Mitigación aplicada o prevista |
| --- | --- |
| Alteración o borrado de evidencia | Triggers SQLite, eventos inmutables y hashes encadenados. |
| No identificar al revisor | Registro de `actor_id` y encabezado `X-User-Id`. |
| Pérdida al reiniciar la API | Persistencia SQLite fuera de los DAOs en memoria. |
| Exposición de datos sensibles | Auditoría limitada a contratos, ofertas, reglas y decisiones. |
| Crecimiento del archivo | Retención mínima de dos años y futura política de archivado sin borrado indebido. |
| Falla entre operación y auditoría | Para producción, migrar ambas escrituras a una transacción o patrón outbox. |

## 8. Verificación

```bash
python -m compileall -q .
ruff check dao domain routers services tests main.py
ruff format --check dao domain routers services tests main.py
pytest -q
```

La definición de terminado exige que todos los criterios de aceptación estén
cubiertos, el PR se vincule con `Closes #49` y no se incorporen archivos SQLite,
credenciales ni artefactos generados al repositorio.
