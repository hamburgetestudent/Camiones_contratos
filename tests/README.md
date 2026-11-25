# Suite de Pruebas Unitarias y de Integración — Camiones Contratos

Este documento contiene la referencia completa, comandos y buenas prácticas para ejecutar, depurar y extender los tests del backend.

---

## 1. Estructura de la Carpeta `tests/`

La suite está organizada por módulos funcionales y dominios de la aplicación:

```text
tests/
├── base.py                   # Clase raíz BaseTestCase (utilidades de aserción, temp dirs, etc.)
├── test_login_usuario.py     # Flujos completos de autenticación
├── test_registro_usuario.py  # Flujos integrales de registro y validaciones
├── configuracion/            # Pruebas de configuración de negocio y parámetros
├── contratos/                # Ciclo de vida de contratos, máquina de estados y transiciones
├── onboarding/               # Validación de transportistas, dadores y documentos
├── persistencia/             # Pruebas de acceso a datos y esquema SQLite
├── seguridad/                # Codificación base64url, tokens JWT y criptografía
├── subastas/                 # Publicación de cargas, ofertas y adjudicaciones
└── usuarios/                 # CRUD de usuarios, hashing de contraseñas y validaciones
```

### Clase Base (`tests/base.py`)
Todos los tests heredan de `BaseTestCase` (o de sus subclases de módulo), la cual provee:
- `assertHttpException(status_code, detalle_esperado)`: Context manager para verificar excepciones HTTP de FastAPI.
- `crear_directorio_temporal()`: Crea carpetas aisladas que se limpian automáticamente en el `tearDown`.
- Aislamiento para pruebas en memoria y SQLite temporal.

---

## 2. Comandos de Ejecución

> [!IMPORTANT]
> Todos los comandos deben ejecutarse desde la **raíz del proyecto** (`Camiones_contratos/`) con el entorno virtual activado.

### A. Ejecución Unificada con Medición de Cobertura (Recomendado)

Ejecuta los tests y muestra en consola la tabla detallada de líneas y ramas cubiertas:
```powershell
python run_tests.py
# o bien
npm run test
```

### B. Reporte Interactivo HTML
Genera una interfaz web interactiva en la carpeta `htmlcov/` para auditar visualmente el código (líneas verdes = ejecutadas, líneas rojas = no alcanzadas, amarillas = ramas parciales):
```powershell
python run_tests.py --html
# o bien
npm run test:html
```
Ruta del reporte generado:
`htmlcov/index.html`

### C. Limpieza de Archivos Temporales de Tests
Elimina de forma segura la base de datos `.coverage`, la carpeta `htmlcov/` y cualquier archivo `.cover` residual:
```powershell
python run_tests.py --clean
# o bien
npm run test:clean
```

---

## 3. Ejecución Directa con `unittest` (Filtros Específicos)

> [!TIP]
> Al usar `unittest` nativo, indica `-t .` (top-level directory) para asegurar la resolución correcta de importaciones desde la raíz del proyecto.

### Ejecutar todos los tests:
```powershell
python -m unittest discover -t . -s tests
```

### Ejecutar únicamente un módulo o subcarpeta:
```powershell
# Solo pruebas del módulo de contratos
python -m unittest discover -t . -s tests/contratos

# Solo pruebas de subastas
python -m unittest discover -t . -s tests/subastas

# Solo pruebas de usuarios
python -m unittest discover -t . -s tests/usuarios
```

### Ejecutar un archivo de test específico:
```powershell
python -m unittest tests.contratos.test_crear_contrato
```

### Ejecutar una clase de test o método individual:
```powershell
# Ejecutar una clase específica
python -m unittest tests.contratos.test_crear_contrato.TestCrearContrato

# Ejecutar un único método test
python -m unittest tests.contratos.test_crear_contrato.TestCrearContrato.test_crear_contrato_exitoso
```

---

## 4. Interpretación del Reporte de Cobertura

El reporte generado por `coverage.py` evalúa dos criterios clave:

1. **Cobertura de Líneas (`Line Coverage`):**
   $$\text{Cobertura de Líneas} = \frac{\text{Líneas ejecutadas}}{\text{Líneas ejecutables totales}} \times 100$$
2. **Cobertura de Ramas (`Branch Coverage`):**
   Mide si cada bifurcación lógica (`if / else`, condiciones compuestas) fue evaluada en todos sus caminos posibles (verdadero y falso).

### Columnas de la Tabla:
- **`Stmts`:** Total de sentencias ejecutables en el archivo.
- **`Miss`:** Cantidad de sentencias que ningún test ejecutó.
- **`Branch`:** Total de caminos de decisión lógica en el archivo.
- **`BrPart`:** Ramas parciales (ejemplo: un `if` que solo se evaluó como `True`, pero nunca como `False`).
- **`Cover`:** Porcentaje ponderado de cobertura total.
- **`Missing`:** **Números exactos de línea** que no fueron alcanzados por las pruebas.

### Priorización para nuevos tests:
1. **Prioridad 1:** Archivos con bajo porcentaje en líneas y ramas (ej. `routers/auth_router.py`).
2. **Prioridad 2:** Archivos con alto porcentaje de líneas pero ramas faltantes (`BrPart` > 0). El 90% de líneas puede dar falsa seguridad si las ramas de error no se recorren.
3. **Prioridad 3:** Casos borde de validadores y transiciones de estado.

---

## 5. Buenas Prácticas al Escribir Nuevos Tests

1. **Nombrado:**
   - Los archivos de prueba deben comenzar con `test_*.py`.
   - Los métodos dentro de las clases deben comenzar con `test_*`.
2. **Heredar de `BaseTestCase`:**
   ```python
   from tests.base import BaseTestCase


   class TestMiFuncionalidad(BaseTestCase):
       def setUp(self) -> None:
           super().setUp()
           # Inicialización limpia por cada test

       def test_caso_exitoso(self) -> None:
           self.assertEqual(1, 1)
   ```
3. **Aislamiento:**
   - Evita acoplar tests a bases de datos compartidas o estados persistentes; utiliza siempre DAOs en memoria (`DAOMemoria`) o bases SQLite temporales limpiadas en `setUp`/`tearDown`.
4. **Validación de errores:**
   - Emplea `with self.assertHttpException(400, "detalle"):` para probar los fallos esperados en routers y servicios.


## Expiración de subastas

Las cinco pruebas de `tests/test_subasta_expiracion.py` utilizan una base SQLite temporal por caso. Para simular el vencimiento, actualizan el plazo del contrato y conservan las ofertas existentes. Una oferta tardía se rechaza. Si era una subasta sin ofertas, el servicio confirma su cancelación antes de comunicar el rechazo. Si tenía ofertas, el dador aún puede adjudicarla.

## Bajas administrativas

Las pruebas de `tests/test_panel_admin.py` comprueban la baja lógica de contratos publicados, la conservación de ofertas y la revocación de acceso al eliminar cuentas. También simulan un fallo al escribir el historial para verificar que la baja se revierta. Para ejecutar únicamente estos casos, usa `python -m pytest tests/test_panel_admin.py -q`.

Los intentos de baja de un usuario autenticado sin rol administrativo reciben HTTP 403. El historial identifica al usuario de la sesión y registra el rechazo sin exponer datos del contrato o de la cuenta solicitada.

Desde `frontend`, ejecuta `npm ci` y `npm run test:panel` para verificar el acceso de los tres roles. Esta prueba usa Playwright con Microsoft Edge, inicia FastAPI con SQLite temporal y comprueba el resumen, una baja administrativa, el historial y el cierre de sesión.
