# Revisión de MansoViaje 1.0.1

| Comprobación | Datos de referencia y resultado esperado |
|---|---|
| Entorno | Windows x64, carpeta de descarga nueva, permiso de instalación por usuario y puerto local 8000 disponible. |
| Archivo | [MansoViaje-1.0.1-win-x64.exe](https://github.com/hamburgetestudent/Camiones_contratos/releases/download/v1.0.1/MansoViaje-1.0.1-win-x64.exe). SHA-256 esperado: `6BEFC25FC86D18AC70139F4C3B54A0D28EF618D0F2E30C24406C237B90866B73`. Commit en `resources/entrega/VERSION.txt`: `7858b4b4bc39cd7fefbf8b57f1928334b05beb66`. |
| Instalación y arranque | El instalador incluye Electron y FastAPI. Al abrir MansoViaje aparece Login sin preparar Python ni Node. El README, las fuentes y la ficha están en `resources/entrega/` junto al ejecutable instalado. |
| Publicación | Con el dador aprobado se crea y publica una carga. Se anota el ID asignado en esa instalación para comprobar después la misma carga. |
| Validación de tarifa | Con el transportista aprobado del README, ingresar 4.900 CLP. El formulario indica un mínimo de 5.000 CLP. La carga sigue publicada y conserva sus ofertas previas. |
| Documentación pendiente | La captura aportada muestra una carga publicada, el indicador KYC PENDIENTE y el aviso para completar documentos. Para el caso válido se utiliza la cuenta aprobada del README. |
| Postulación y persistencia | Enviar 180.000 CLP como transportista aprobado. Cerrar y reabrir la aplicación. Como dador, consultar el mismo ID: se espera una oferta por 180.000 CLP en `POSTULADA` y un contrato en `EN_POSTULACION`. |
| Punto de extensión | Para ampliar el comentario a 600 caracteres, ajustar el límite en `backend/app/modules/subastas/models.py` y en `frontend/src/paginas/panel/vistas/transportista/subastas.js`. Agregar casos en `backend/tests/subastas/test_modelos_postulacion.py` para aceptar 600 y rechazar 601. |

**Evidencia externa disponible:** captura de la pantalla de carga con KYC pendiente.

**Pendiente de registrar:** fecha y versión de Windows de la prueba, hash obtenido, ID de la carga, lectura de la oferta después del reinicio, localización del punto de extensión y cualquier paso que requirió ayuda. Si hubo una corrección, anotar el cambio y el resultado de repetir ese paso.
