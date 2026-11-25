# Componente propio reutilizable: `UsuarioService`

Archivo: [services/usuario_service.py](../services/usuario_service.py). Fachada de casos de uso de usuarios (registro, consulta, autenticación, sesión). Persiste mediante un DAO inyectable (`UsuarioDAO`) y comunica errores propios de negocio (`CorreoYaRegistradoError`, `CredencialesInvalidasError`, `UsuarioNoEncontradoError`, `ValueError`), sin acoplarse a HTTP ni a `fastapi`. La traducción a códigos HTTP (`400`, `401`, `404`) recae en [routers/auth_router.py](../routers/auth_router.py).

## Contrato

| Operación | Entrada | Salida | Errores de negocio (servicio) | Traducción HTTP (router) | Precondición / postcondición |
|---|---|---|---|---|---|
| `registrar_usuario(usuario_data)` | `UsuarioCrear` ya validado (correo con email-validator, rol, clave ≥ 6) | `UsuarioModelo` | `CorreoYaRegistradoError("El email ya está registrado")` | `400` con mismo mensaje | Email único (comprobación y guardado en una sola transacción). Se guarda `password_hash`, nunca la clave en claro. Documentos o perfil tributario quedan en PENDIENTE. |
| `listar_usuarios()` | — | `list[UsuarioModelo]` | — | `200` | Solo lectura. |
| `obtener_usuario(usuario_id)` | `UUID` | `UsuarioModelo` | `UsuarioNoEncontradoError("Usuario no encontrado")` | `404` con mismo mensaje | Solo lectura. |
| `autenticar_usuario(email, password)` | `str`, `str` | `UsuarioModelo` | `ValueError` si algún campo está vacío; `CredencialesInvalidasError("Credenciales inválidas")` | `400` / `401` | No distingue entre email inexistente y clave errónea. |
| `iniciar_sesion(credenciales)` | `CredencialesLogin` | `RespuestaLogin` (token Bearer) | `ValueError` si faltan campos; `CredencialesInvalidasError("Credenciales inválidas")` | `400` / `401` con mismo mensaje | Usa `autenticar_usuario` y emite el token con `services.respuesta_login` y `services.security`. |

**Punto de extensión:** el atributo de clase `dao` (`UsuarioService.dao = UsuarioDAOSQLite(ruta)`) permite sustituir el almacenamiento, por ejemplo una base aislada en pruebas.

## Uso real (reutilización)

- [routers/auth_router.py](../routers/auth_router.py): login, registro, listado y consulta por id expuestos por la API, traduciendo los errores del servicio a respuestas HTTP en `_ejecutar_usuario_http`.
- [services/sesion_service.py](../services/sesion_service.py): `resolver_usuario_desde_token` reutiliza `UsuarioService.dao` para resolver el usuario del token.
- [services/dependencies.py](../services/dependencies.py): inyecta el DAO compartido en el servicio.
- Dentro de la propia clase, `iniciar_sesion` reutiliza `autenticar_usuario`.

## Evidencia

Pruebas en [tests/usuarios/](../tests/usuarios/): `test_registrar_usuario.py`, `test_autenticar_usuario.py`, `test_iniciar_sesion.py`, `test_listar_usuarios.py`, `test_obtener_usuario.py` y `test_router_auth.py` (traducción HTTP en endpoints). Ejecutar: `python -m unittest discover -s tests -t .`

Reutiliza además la dependencia externa documentada en [revision-dependencia-email-validator.md](revision-dependencia-email-validator.md).
