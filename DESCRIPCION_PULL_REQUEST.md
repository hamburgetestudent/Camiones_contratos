# Login backend con usuario y contraseña

## Qué incluye

- Modelo de entrada con `usuario` y `password`.
- Endpoint `POST /auth/login`.
- Servicio que delega la comprobación al validador del equipo.
- Respuestas HTTP `200` y `401`.
- Pruebas automatizadas del flujo de login.

## Fuera de alcance

- Registro de usuarios.
- Reglas de validación de credenciales.
- Persistencia o consultas a base de datos.
- Hash de contraseñas.
- Creación de tokens o sesiones.

## Integración pendiente

Conectar `crear_login_router(...)` con el objeto validador desarrollado por el
compañero responsable. El validador debe implementar
`validar(usuario: str, password: str) -> bool`.

## Verificación

Ejecutar:

```bash
python -m pytest -q
```

