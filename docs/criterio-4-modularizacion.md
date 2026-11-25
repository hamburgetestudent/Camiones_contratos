# Criterio 4: Modularización de las interfaces y dependencias

## Objetivo

Separar la autenticación del usuario de la construcción de la respuesta de inicio de sesión, manteniendo el comportamiento funcional del sistema.

## Situación anterior

UsuarioService.iniciar_sesion concentraba la validación de credenciales, la autenticación, la preparación de los datos del usuario y la construcción de la respuesta con el token JWT.

## Modularización aplicada

Se creó el módulo `backend/app/modules/usuarios/respuesta_login.py`, responsable de construir la respuesta de un usuario autenticado.

UsuarioService conserva la validación y autenticación, delegando la construcción de la respuesta al nuevo módulo.

## Operaciones públicas y dependencias

| Módulo | Operación pública | Responsabilidad |
|---|---|---|
| backend/app/modules/usuarios/router.py | iniciar_sesion(credenciales) | Recibe la solicitud HTTP |
| backend/app/modules/usuarios/service.py | iniciar_sesion(credenciales) | Valida, autentica y delega |
| backend/app/modules/usuarios/service.py | autenticar_usuario(email, password) | Verifica las credenciales |
| backend/app/modules/usuarios/respuesta_login.py | construir_respuesta_login(usuario) | Construye RespuestaLogin |
| backend/app/backend/app/core/security.py | crear_token_acceso(claims) | Genera el token JWT |

El nuevo módulo recibe un UsuarioModelo y devuelve una RespuestaLogin. Depende de los modelos de dominio y del módulo de seguridad, sin depender de UsuarioService.

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

Resultados obtenidos el 24 de noviembre de 2026, utilizando Python 3.12 y el entorno virtual venv.

- Antes de modularizar: 2 pruebas exitosas.
- Después de modularizar: las mismas 2 pruebas exitosas.
- Pruebas específicas finales: 4 exitosas.
- Pruebas generales de usuarios: 26 exitosas.
- Suite general del proyecto: 213 pruebas exitosas, sin errores.
- Verificaciones automáticas de backend y frontend del PR #126: exitosas.

Se verificó el inicio de sesión para transportistas, dadores de carga y administradores, la generación del token, la colaboración entre módulos y el rechazo de credenciales incorrectas.

## Archivos relacionados

- [Servicio de usuarios](../backend/app/modules/usuarios/service.py)
- [Constructor de respuesta](../backend/app/modules/usuarios/respuesta_login.py)
- [Seguridad](../backend/app/backend/app/core/security.py)
- [Router de autenticación](../backend/app/modules/usuarios/router.py)
- [Pruebas](../backend/tests/usuarios/test_iniciar_sesion.py)

## Ubicación exacta de los cambios

| Archivo | Operación | Líneas |
|---|---|---|
| backend/app/modules/usuarios/router.py | iniciar_sesion | 46-48 |
| backend/app/modules/usuarios/service.py | iniciar_sesion | 193-215 |
| backend/app/modules/usuarios/respuesta_login.py | Dependencias | 3-5 |
| backend/app/modules/usuarios/respuesta_login.py | construir_respuesta_login | 8 |
| backend/app/modules/usuarios/respuesta_login.py | Solicitud del token | 19-25 |
| backend/app/modules/usuarios/respuesta_login.py | Construcción de respuesta | 27-37 |
| backend/app/backend/app/core/security.py | crear_token_acceso | 36 |
| backend/tests/usuarios/test_iniciar_sesion.py | Prueba de caracterización | 33-61 |
| backend/tests/usuarios/test_iniciar_sesion.py | Prueba de colaboración | 63-98 |
| backend/tests/usuarios/test_iniciar_sesion.py | Credenciales inválidas | 100-117 |

Las líneas corresponden al commit c05f5e1.

## Fragmento principal de la modularización

```python
usuario = UsuarioService.autenticar_usuario(email, password)
return construir_respuesta_login(usuario)
```

La primera instrucción autentica al usuario. La segunda delega la construcción de la respuesta.

## Contrato de la nueva operación pública

```python
def construir_respuesta_login(usuario: UsuarioModelo) -> RespuestaLogin:
```

- Entrada: un UsuarioModelo previamente autenticado.
- Salida: RespuestaLogin con los datos del usuario y token JWT.
- Precondición: el usuario debe estar autenticado.
- Dependencias: modelos de dominio y app.core.security.
- Consumidor: UsuarioService.iniciar_sesion.
- Credenciales incorrectas: UsuarioService genera un error HTTP 401 sin invocar el constructor.
- El constructor no valida contraseñas ni consulta la base de datos.

## Indicadores comparables

Alcance: flujo de inicio de sesión del backend.

| Indicador | Antes | Después |
|---|---|---|
| Módulo de construcción de respuesta independiente | 0 | 1 |
| Operación pública de inicio de sesión conservada | 1 | 1 |
| Mismas pruebas de caracterización aprobadas | 2/2 | 2/2 |

La mejora consiste en separar responsabilidades sin modificar el contrato observable del inicio de sesión.

## Pruebas que demuestran la colaboración

- test_inicio_sesion_exitoso_emite_token_y_rol
- test_inicio_sesion_todos_los_roles
- test_colaboracion_entre_modulos
- test_credenciales_invalidas_no_construyen_respuesta

Las pruebas de colaboración verifican que el servicio invoca el nuevo constructor, que este solicita el token al módulo de seguridad y que las credenciales incorrectas impiden invocar el constructor.

## Conclusión

La modularización separa responsabilidades mediante operaciones públicas y dependencias explícitas. Las pruebas ejecutadas demuestran que los módulos colaboran correctamente y conservan el comportamiento evaluado.

---

## Comandos paso a paso

### 1. Código antes y después

```bash
git --no-pager diff c3081be c05f5e1 -- backend/app/modules/usuarios/service.py
```

### 2. Activar entorno

```bash
source venv/bin/activate
python --version
```

### 3. Pruebas antes y después

```bash
(
set -e
set -o pipefail

PYTHON="$PWD/venv/bin/python"
TEMP=$(mktemp -d)
trap 'rm -rf -- "$TEMP"' EXIT

mkdir -p "$TEMP/antes" "$TEMP/despues"

git archive c3081be | tar -x -C "$TEMP/antes"
git archive c05f5e1 | tar -x -C "$TEMP/despues"

cp "$TEMP/despues/tests/usuarios/test_iniciar_sesion.py" \
   "$TEMP/antes/tests/usuarios/test_iniciar_sesion.py"

CASO=tests.usuarios.test_iniciar_sesion.TestIniciarSesion

echo "===== ANTES DE MODULARIZAR ====="

(cd "$TEMP/antes" && "$PYTHON" -m unittest -v \
 "$CASO.test_inicio_sesion_exitoso_emite_token_y_rol" \
 "$CASO.test_inicio_sesion_todos_los_roles")

echo "===== DESPUES DE MODULARIZAR ====="

(cd "$TEMP/despues" && "$PYTHON" -m unittest -v \
 "$CASO.test_inicio_sesion_exitoso_emite_token_y_rol" \
 "$CASO.test_inicio_sesion_todos_los_roles")
)
```

### 4. Pruebas de inicio de sesión (4)

```bash
python -m unittest -v tests.usuarios.test_iniciar_sesion
```

### 5. Pruebas de usuarios (26)

```bash
python -m unittest discover -s backend/tests/usuarios -t . -v
```

### 6. Pruebas generales (213)

```bash
python -m unittest discover -s tests -t . -v
```