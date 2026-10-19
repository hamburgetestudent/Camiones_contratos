
# Tabla de verificación – Registro de usuarios

**Asignatura:** Taller de Programación Avanzada ISF224  
**Unidad:** 2.2 – Construcción para la verificación  
**Proyecto:** Camiones_contratos  
**Funcionalidad seleccionada:** Registro de usuarios  

## Ficha de operación: Registro de usuarios

Esta ficha documenta las precondiciones, postcondiciones, invariantes, validaciones defensivas y dependencias explícitas de la funcionalidad seleccionada.

| Elemento | Registro del equipo |
|---|---|
| **Funcionalidad y operación** | **Registro de usuario:** `UsuarioService.registrar_usuario(usuario_data, dao=None)`.<br><br>**Ruta HTTP:** `POST /auth/registro`.<br><br>**Archivos relacionados:**<br>• `services/usuario_service.py`<br>• `domain/modelos_usuario.py`<br>• `dao/usuario_dao.py`<br>• `routers/auth_router.py` |
| **Propósito** | Crear una cuenta nueva validando sus datos, comprobando que el correo no esté registrado, generando el hash de la contraseña y devolviendo los datos públicos del usuario creado. |
| **Precondiciones** | **1.** El nombre tiene al menos 2 caracteres; el correo tiene formato válido; la contraseña tiene al menos 6 caracteres y el rol pertenece a `RolUsuario`.<br><br>**2.** El correo no existe previamente en el `UsuarioDAO` y el repositorio de usuarios está disponible. |
| **Postcondiciones** | **1.** Se guarda un `UsuarioModelo` con UUID, nombre, correo, rol y `password_hash`; nunca se almacena la contraseña en texto plano.<br><br>**2.** La operación devuelve el usuario creado y la ruta responde con **HTTP 201** sin exponer `password_hash`. |
| **Invariante** | La unicidad del correo se conserva sin distinguir mayúsculas y minúsculas; una entrada inválida o duplicada no crea ni reemplaza usuarios existentes. |
| **Validación defensiva** | **Entrada válida:** nombre "Camila Prueba", email `camila.verificacion@example.com`, rol `TRANSPORTISTA` y contraseña `Prueba123`.<br>**Respuesta esperada:** usuario creado, UUID y **HTTP 201**.<br><br>**Entrada inválida 1:** email ya registrado.<br>**Respuesta esperada:** **HTTP 400**, "El email ya está registrado", sin guardar.<br><br>**Entrada inválida 2:** contraseña `123` o nombre compuesto solo por espacios.<br>**Respuesta esperada:** **HTTP 422** por validación Pydantic, sin guardar. |
| **Dependencia explícita** | `UsuarioDAO`, inyectado mediante el parámetro opcional `dao`; si no se entrega, se utiliza el DAO en memoria global.<br><br>En pruebas se reemplaza por `UsuarioDAOMemoria` independiente para controlar consultas y guardados. |
| **Evidencia de ejecución** | **Archivo de pruebas:** `tests/test_registro_usuario.py`.<br><br>**Comando:**<br>`python -m pytest tests/test_registro_usuario.py -v`<br><br>**Evidencias que deben adjuntarse:**<br>• Captura del caso exitoso **HTTP 201**.<br>• Captura del correo duplicado **HTTP 400**.<br>• Captura de la validación **HTTP 422**.<br>• Salida real de las pruebas ejecutadas con `pytest`. |

## Evidencias pendientes de adjuntar

- [ ] Captura del registro exitoso con HTTP 201.
- [ ] Captura del intento de registro con correo duplicado, HTTP 400.
- [ ] Captura de entrada inválida, HTTP 422.
- [ ] Resultado de la ejecución de `pytest`.
- [ ] Confirmación de que las validaciones y la dependencia explícita funcionan en el código del proyecto.

**Nota:** Las respuestas descritas en la tabla representan los resultados esperados según la ficha de operación. Las evidencias deben incorporarse después de ejecutar y comprobar los casos correspondientes.
