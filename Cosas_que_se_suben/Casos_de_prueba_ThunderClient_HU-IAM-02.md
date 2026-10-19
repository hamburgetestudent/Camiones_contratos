# Casos de Prueba para APIs con Thunder Client (HU-IAM-02: Iniciar Sesión)

Este documento detalla la suite y matriz de casos de prueba para el endpoint `POST /auth/login` diseñados para ejecutarse en **Thunder Client** (VS Code) o cualquier cliente HTTP REST compatible.

---

## 1. Identificación y Trazabilidad

- **Historia de Usuario**: HU-IAM-02 – Iniciar sesión
- **Issue Asociado**: [#51 - HU-IAM-02: Inicio de Sesión y Emisión de Credenciales](https://github.com/hamburgetestudent/Camiones_contratos/issues/51)
- **Endpoint Objetivo**: `POST /auth/login`
- **Mecanismo de Autenticación**: OAuth2 con token de acceso tipo Bearer
- **Colección de Pruebas**: `thunder-tests/postman-collection_HU-IAM-02-Login.json` (Formato Postman 2.1.0 compatible con Thunder Client, Postman e Insomnia)
- **Ambiente de Variables**: `thunder-tests/postman-environment_Local.json` (`base_url = http://127.0.0.1:8000`)

---

## 2. Instrucciones para Importar y Ejecutar en Thunder Client

1. Abrir **Visual Studio Code**.
2. Ir a la pestaña de la extensión **Thunder Client** (icono de rayo ⚡ en la barra lateral izquierda).
3. En la sección **Collections**, hacer clic en el menú contextual de tres puntos (`...`) y seleccionar **Import**.
4. Seleccionar el archivo:
   ```
   thunder-tests/postman-collection_HU-IAM-02-Login.json
   ```
5. En la sección **Environments**, hacer clic en `...` -> **Import** y seleccionar:
   ```
   thunder-tests/postman-environment_Local.json
   ```
6. Activar el ambiente **Local (FastAPI 8000)** en el selector superior derecho de Thunder Client.
7. Asegurarse de que el backend de FastAPI esté en ejecución:
   ```powershell
   python main.py
   ```
8. En la colección importada, selecciona y ejecuta cada petición individual con el botón **Send** para ver la respuesta del servidor y validar que todas las aserciones de prueba en la pestaña **Tests** pasen en verde.

---

## 3. Matriz de Casos de Prueba

### Carpeta 1: CA1 – Inicio de Sesión Exitoso

| ID Caso | Nombre / Propósito | Método y Endpoint | Payload de Entrada | Status Esperado | Assertions Thunder Client |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **CA1-01** | Login exitoso Transportista | `POST /auth/login` | `{"email": "juan.perez@rutanorte.cl", "password": "camion123"}` | `200 OK` | `res.status == 200`<br>`json.token_type == bearer`<br>`json.rol == TRANSPORTISTA`<br>`json.access_token isNotEmpty` |
| **CA1-02** | Login exitoso Dador de Carga | `POST /auth/login` | `{"email": "contacto@logisticasur.cl", "password": "dador123"}` | `200 OK` | `res.status == 200`<br>`json.token_type == bearer`<br>`json.rol == DADOR_CARGA`<br>`json.access_token isNotEmpty` |
| **CA1-03** | Compatibilidad con alias `usuario` | `POST /auth/login` | `{"usuario": "juan.perez@rutanorte.cl", "password": "camion123"}` | `200 OK` | `res.status == 200`<br>`json.token_type == bearer`<br>`json.access_token isNotEmpty` |
| **CA1-04** | Insensibilidad a mayúsculas | `POST /auth/login` | `{"email": "JUAN.PEREZ@RUTANORTE.CL", "password": "camion123"}` | `200 OK` | `res.status == 200`<br>`json.token_type == bearer` |

---

### Carpeta 2: CA2 – Credenciales Incorrectas

| ID Caso | Nombre / Propósito | Método y Endpoint | Payload de Entrada | Status Esperado | Assertions Thunder Client |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **CA2-01** | Contraseña incorrecta | `POST /auth/login` | `{"email": "juan.perez@rutanorte.cl", "password": "claveTotalmenteErronea"}` | `401 Unauthorized` | `res.status == 401`<br>`json.detail == Credenciales inválidas` |
| **CA2-02** | Correo no registrado | `POST /auth/login` | `{"email": "fantasma.inexistente@correo.cl", "password": "passwordValida123"}` | `401 Unauthorized` | `res.status == 401`<br>`json.detail == Credenciales inválidas` |

---

### Carpeta 3: CA3 – Validación de Campos Obligatorios

| ID Caso | Nombre / Propósito | Método y Endpoint | Payload de Entrada | Status Esperado | Assertions Thunder Client |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **CA3-01** | Omisión de correo electrónico | `POST /auth/login` | `{"password": "camion123"}` | `422 Unprocessable` | `res.status == 422` |
| **CA3-02** | Omisión de contraseña | `POST /auth/login` | `{"email": "juan.perez@rutanorte.cl"}` | `422 Unprocessable` | `res.status == 422` |
| **CA3-03** | Correo electrónico vacío `""` | `POST /auth/login` | `{"email": "", "password": "camion123"}` | `422 Unprocessable` | `res.status == 422` |
| **CA3-04** | Contraseña vacía `""` | `POST /auth/login` | `{"email": "juan.perez@rutanorte.cl", "password": ""}` | `422 Unprocessable` | `res.status == 422` |
| **CA3-05** | Cuerpo JSON vacío `{}` | `POST /auth/login` | `{}` | `422 Unprocessable` | `res.status == 422` |

---

### Carpeta 4: CA4 – Visualización y Rol del Usuario

| ID Caso | Nombre / Propósito | Método y Endpoint | Payload de Entrada | Status Esperado | Assertions Thunder Client |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **CA4-01** | Verificación Rol Administrador | `POST /auth/login` | `{"email": "admin@camiones.cl", "password": "admin123"}` | `200 OK` | `res.status == 200`<br>`json.rol == ADMIN_BACKOFFICE`<br>`json.token_type == bearer` |

---

## 4. Usuarios Semilla Preconfigurados en SQLite (`camiones.db`)

| Email | Contraseña | Rol Asignado | Estado Operativo |
| :--- | :--- | :--- | :--- |
| `juan.perez@rutanorte.cl` | `camion123` | `TRANSPORTISTA` | `APROBADO` |
| `carlos.soto@transporte.cl` | `carlos123` | `TRANSPORTISTA` | `EN_REVISION` |
| `contacto@logisticasur.cl` | `dador123` | `DADOR_CARGA` | `APROBADO` |
| `operaciones@vallecentral.cl` | `valle123` | `DADOR_CARGA` | `EN_REVISION` |
| `admin@camiones.cl` | `admin123` | `ADMIN_BACKOFFICE` | `APROBADO` |

