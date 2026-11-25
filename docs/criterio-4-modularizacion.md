# Criterio 4: Modularización de las interfaces y dependencias

## Objetivo

Separar la autenticación del usuario de la construcción de
la respuesta de inicio de sesión, manteniendo el comportamiento
funcional del sistema.

## Situación anterior

UsuarioService.iniciar_sesion concentraba la validación de
credenciales, la autenticación, la preparación de los datos
del usuario y la construcción de la respuesta con el token JWT.

Versión base: commit c3081be, sincronizado con Dev.

## Modularización aplicada

Se creó el módulo backend/app/modules/usuarios/respuesta_login.py, responsable
de construir la respuesta de un usuario autenticado.

UsuarioService conserva la validación y autenticación,
delegando la construcción de la respuesta al nuevo módulo.

## Operaciones públicas y dependencias

| Módulo | Operación pública | Responsabilidad |
|---|---|---|
| backend/app/modules/usuarios/router.py | iniciar_sesion(credenciales) | Recibe la solicitud HTTP |
| backend/app/modules/usuarios/service.py | iniciar_sesion(credenciales) | Valida, autentica y delega |
| backend/app/modules/usuarios/service.py | autenticar_usuario(email, password) | Verifica las credenciales |
| backend/app/modules/usuarios/respuesta_login.py | construir_respuesta_login(usuario) | Construye RespuestaLogin |
| backend/app/core/security.py | crear_token_acceso(claims) | Genera el token JWT |

El nuevo módulo recibe un UsuarioModelo y devuelve una
RespuestaLogin. Depende de los modelos de dominio y del
módulo de seguridad, sin depender de UsuarioService.

## Colaboración entre módulos

1. El router recibe las credenciales.
2. UsuarioService valida y autentica al usuario.
3. UsuarioService entrega el usuario autenticado al constructor.
4. El constructor solicita el token al módulo de seguridad.
5. El constructor devuelve la respuesta de inicio de sesión.

Si las credenciales son inválidas, no se invoca el constructor.

## Comparación antes y después

| Aspecto | Antes | Después |
|---|---|---|
| Construcción de respuesta | Dentro de UsuarioService | Módulo independiente |
| Responsabilidades | Concentradas | Separadas |
| Contrato de inicio de sesión | RespuestaLogin | Sin cambios |
| Pruebas de caracterización | 2 exitosas | 2 exitosas |

## Evidencia de pruebas

Resultados obtenidos el 24 de noviembre de 2026,
utilizando Python 3.12 y el entorno virtual venv.

- Antes de modularizar: 2 pruebas exitosas.
- Después de modularizar: las mismas 2 pruebas exitosas.
- Pruebas específicas finales: 4 exitosas.
- Pruebas generales de usuarios: 26 exitosas.
- Suite general del proyecto: 213 pruebas exitosas, sin errores.

Se verificó el inicio de sesión para transportistas,
dadores de carga y administradores, la generación del token,
la colaboración entre módulos y el rechazo de credenciales
incorrectas.

## Reproducción de pruebas

Desde la raíz del repositorio:

```bash
source venv/bin/activate
python -m unittest -v tests.usuarios.test_iniciar_sesion
python -m unittest discover -s backend/tests/usuarios -t backend -v
```

## Archivos relacionados

- [Servicio de usuarios](../backend/app/modules/usuarios/service.py)
- [Constructor de respuesta](../backend/app/modules/usuarios/respuesta_login.py)
- [Seguridad](../backend/app/core/security.py)
- [Router de autenticación](../backend/app/modules/usuarios/router.py)
- [Pruebas](../backend/tests/usuarios/test_iniciar_sesion.py)

## Conclusión

La modularización separa responsabilidades mediante
operaciones públicas y dependencias explícitas.
Las pruebas ejecutadas demuestran que los módulos colaboran
correctamente y conservan el comportamiento evaluado.

## Ubicacion exacta de los cambios

| Archivo | Operacion que se debe revisar |
|---|---|
| backend/app/modules/usuarios/service.py | UsuarioService.iniciar_sesion |
| backend/app/modules/usuarios/respuesta_login.py | construir_respuesta_login |
| backend/app/core/security.py | crear_token_acceso |
| backend/app/modules/usuarios/router.py | iniciar_sesion |
| backend/tests/usuarios/test_iniciar_sesion.py | TestIniciarSesion |

### Fragmento principal de la modularizacion

```python
usuario = UsuarioService.autenticar_usuario(email, password)
return construir_respuesta_login(usuario)
```

La primera instruccion autentica al usuario.
La segunda delega la construccion de la respuesta.

### Contrato de la nueva operacion publica

```python
def construir_respuesta_login(usuario: UsuarioModelo) -> RespuestaLogin:
```

- Entrada: un UsuarioModelo previamente autenticado.
- Salida: RespuestaLogin con los datos del usuario y token JWT.
- Precondicion: el usuario debe estar autenticado.
- Dependencias: modelos de dominio y app.core.security.
- Consumidor: UsuarioService.iniciar_sesion.
- Credenciales incorrectas: UsuarioService retorna HTTP 401
  sin invocar el constructor.
- El constructor no valida contrasenas ni consulta la base de datos.

## Relacion con los contenidos de la Unidad 3

| Clase | Concepto aplicado |
|---|---|
| 3.1 | Extraccion de una operacion y pruebas de caracterizacion |
| 3.2 | Responsabilidades mezcladas y comparacion antes/despues |
| 3.3 | Cohesion, interfaz publica y compatibilidad |

## Indicadores comparables

Alcance: flujo de inicio de sesion del backend.

| Indicador | Antes | Despues |
|---|---|---|
| Modulo de construccion de respuesta independiente | 0 | 1 |
| Operacion publica de inicio de sesion conservada | 1 | 1 |
| Mismas pruebas de caracterizacion aprobadas | 2/2 | 2/2 |

La mejora consiste en separar responsabilidades sin
modificar el contrato observable del inicio de sesion.

## Verificacion general

```bash
python -m unittest discover -s backend/tests -t backend -v
```

Resultado registrado: 213 pruebas exitosas, sin errores.

## Pruebas que demuestran la colaboracion

- test_inicio_sesion_exitoso_emite_token_y_rol
- test_inicio_sesion_todos_los_roles
- test_colaboracion_entre_modulos
- test_credenciales_invalidas_no_construyen_respuesta

Las pruebas de colaboracion verifican que el servicio
invoca el nuevo constructor, que este solicita el token
al modulo de seguridad y que las credenciales incorrectas
impiden invocar el constructor.
