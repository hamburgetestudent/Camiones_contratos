# Componente propio reutilizable: `UsuarioService`

Archivo: [services/usuario_service.py](../services/usuario_service.py). Fachada de casos de uso de usuarios (registro, consulta, autenticación, sesión). Persiste mediante un DAO inyectable (`UsuarioDAO`) y no conoce HTTP más allá de lanzar `HTTPException`.

## Contrato

| Operación | Entrada | Salida | Errores | Precondición / postcondición |
|---|---|---|---|---|
| `registrar_usuario(usuario_data)` | `UsuarioCrear` ya validado (correo con email-validator, rol, clave ≥ 6) | `UsuarioModelo` | 400 `El email ya está registrado` | Email único (comprobación y guardado en una sola transacción). Se guarda `password_hash`, nunca la clave en claro. Documentos o perfil tributario quedan en PENDIENTE. |
| `listar_usuarios()` | — | `list[UsuarioModelo]` | — | Solo lectura. |
| `obtener_usuario(usuario_id)` | `UUID` | `UsuarioModelo` | 404 `Usuario no encontrado` | Solo lectura. |
| `autenticar_usuario(email, password)` | `str`, `str` | `UsuarioModelo` | 400 si alguno está vacío; 401 `Credenciales inválidas` | No distingue entre email inexistente y clave errónea. |
| `iniciar_sesion(credenciales)` | `CredencialesLogin` | `RespuestaLogin` (token Bearer) | 400 campos obligatorios; 401 | Usa `autenticar_usuario` y emite el token con `services.security`. |

**Punto de extensión:** el atributo de clase `dao` (`UsuarioService.dao = UsuarioDAOSQLite(ruta)`) permite sustituir el almacenamiento, por ejemplo una base aislada en pruebas.

## Uso real (reutilización)

- [routers/auth_router.py:48,59,71,83](../routers/auth_router.py): login, registro, listado y consulta por id expuestos por la API.
- [routers/sesion.py:37](../routers/sesion.py): `usuario_actual` reutiliza `UsuarioService.dao` para resolver el usuario del token.
- [services/dependencies.py:30](../services/dependencies.py): inyecta el DAO compartido en el servicio.
- Dentro de la propia clase, `iniciar_sesion` reutiliza `autenticar_usuario`.

## Evidencia

Pruebas en [tests/usuarios/](../tests/usuarios/): `test_registrar_usuario.py`, `test_autenticar_usuario.py`, `test_iniciar_sesion.py`, `test_listar_usuarios.py`, `test_obtener_usuario.py` y `test_router_auth.py` (uso desde el router). Ejecutar: `python -m unittest discover -s tests -t .`

Reutiliza además la dependencia externa documentada en [revision-dependencia-email-validator.md](revision-dependencia-email-validator.md).
