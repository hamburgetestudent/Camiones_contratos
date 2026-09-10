# Guía de Contribución y Convención de Estilo Backend

Este documento establece las directrices de calidad de código, formato y estilo obligatorias para colaborar en el backend del proyecto **Camiones Contratos**, de acuerdo con los criterios de evaluación **E4 (Calidad de Código, Linting y Documentación)**.

---

## 1. Herramientas de Calidad de Código: Ruff

Para garantizar un código homogéneo, limpio y libre de errores en tiempo de ejecución, el proyecto utiliza **[Ruff](https://docs.astral.sh/ruff/)** como linter y formateador oficial para **Python 3.12**.

Ruff reemplaza herramientas individuales como Flake8, Black, isort y pyupgrade con una velocidad significativamente superior.

### Instalación de dependencias de desarrollo

Asegúrate de instalar las dependencias de desarrollo antes de enviar código:

```bash
pip install -r requirements-dev.txt
# o instalar ruff directamente:
pip install ruff>=0.4.0
```

---

## 2. Ejecución Local de Ruff

Antes de realizar un commit o abrir un Pull Request, debes ejecutar las siguientes revisiones:

### Comprobación de errores y estilo (Linter)
```bash
# Inspeccionar todo el proyecto
ruff check .

# Aplicar correcciones automáticas seguras
ruff check --fix .
```

### Formateo consistente de código (Formatter)
```bash
# Formatear todos los archivos según la convención del proyecto
ruff format .

# Verificar si los archivos cumplen con el formato sin modificarlos (útil para CI)
ruff format --check .
```

---

## 3. Configuración y Reglas Habilitadas

Nuestra configuración se encuentra centralizada en `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP"]

[tool.ruff.format]
quote-style = "double"
```

### Explicación de las Reglas Habilitadas:

| Código | Conjunto de Reglas | Propósito y Utilidad |
| :---: | :--- | :--- |
| **E** | `pycodestyle` (Errors) | Detecta violaciones al estándar **PEP 8**, como sangrías erróneas, espacios en blanco superfluos o líneas excesivamente largas (> 120 caracteres). |
| **W** | `pycodestyle` (Warnings) | Avisos de advertencias según PEP 8 (ej. líneas en blanco consecutivas excesivas, tabulaciones mixtas). |
| **F** | `Pyflakes` | Detección de fallos lógicos graves: imports no utilizados, variables indefinidas (`NameError`), variables nunca usadas y redefinición accidental de funciones o clases. |
| **I** | `isort` | Ordena y agrupa los imports automáticamente en 3 secciones separadas por línea en blanco: Librería estándar, Dependencias de terceros (FastAPI, Pydantic) y Módulos locales. |
| **N** | `pep8-naming` | Valida convenciones de nomenclatura: clases en `PascalCase`, funciones/variables en `snake_case`, y constantes en `UPPER_CASE`. |
| **UP** | `pyupgrade` | Actualiza la sintaxis automáticamente a las características modernas de **Python 3.12** (por ejemplo, simplificación de anotaciones y formatos de cadenas). |

---

## 4. Ejemplo Práctico: "Antes / Después" con Ruff

A continuación se muestra un ejemplo típico de código desordenado con imports mezclados, sintaxis obsoleta y variables no usadas, y cómo Ruff lo corrige:

### ❌ Antes (con advertencias de F401, I001, UP006, E302):
```python
import sys
from typing import List, Dict
import os
from datetime import datetime


def calcular_totales(items: List[Dict[str, float]]) -> float:
    descuento_aplicado = 0.05
    total = 0
    for item in items:
        total += item["precio"]
    return total
```

### ✅ Después (`ruff check --fix .` y `ruff format .`):
```python
from datetime import datetime
import os
import sys


def calcular_totales(items: list[dict[str, float]]) -> float:
    total = 0.0
    for item in items:
        total += item["precio"]
    return total
```
*Mejoras aplicadas por Ruff:*
1. **Regla `I001`**: Ordenó los imports de la biblioteca estándar alfabéticamente.
2. **Regla `F401`**: Eliminó la variable o importación innecesaria.
3. **Regla `UP006`**: Reemplazó `List`/`Dict` de `typing` por los tipos genéricos nativos `list`/`dict` de Python 3.12.
4. **Formato**: Ajustó el espaciado alrededor de operadores aritméticos y argumentos (`total += item["precio"]`).

---

## 5. Casos Reales Corregidos gracias al Análisis Estático (Para Evaluación E4)

Durante la auditoría con Ruff sobre la rama `Dev`, se identificaron y solucionaron los siguientes **bugs críticos en tiempo de ejecución**:

### Caso 1: `NameError` en validación de Carga Peligrosa (`domain/modelos.py`)
- **Regla detectada:** `F821 Undefined name 're'`
- **Problema:** Se compilaba una expresión regular en la línea 21 (`ONU_REGEX = re.compile(r"^(UN)?\d{4}$")`) pero `import re` nunca había sido importado. Al instanciar cualquier contrato con carga peligrosa, el backend fallaba con `NameError: name 're' is not defined`.
- **Solución aplicada:** Se importó el módulo `re` en el encabezado del archivo.

### Caso 2: Manejo de errores roto en routers (`routers/contratos_router.py`)
- **Regla detectada:** `F821 Undefined name 'HTTPException'`, `Undefined name 'ValidationError'`
- **Problema:** En el bloque `except (ValueError, ValidationError): raise HTTPException(...)` ni `HTTPException` ni `ValidationError` habían sido importados. Cuando ocurría un error de validación, la API colapsaba con un error 500 no controlado en lugar del 400 Bad Request previsto.
- **Solución aplicada:** Se importó `HTTPException` desde `fastapi` y `ValidationError` desde `pydantic`.

### Caso 3: Redefinición accidental y colisión de clase (`dao/usuario_dao.py`)
- **Reglas detectadas:** `F811 Redefinition of unused 'UsuarioDAO'`, `F401 Cannot import name 'BD_DAO'`
- **Problema:** La clase `UsuarioDAO` estaba declarada dos veces en el mismo archivo con interfaces y jerarquías incompatibles, intentando además importar un nombre legado `BD_DAO` inexistente en `dao/base_dao.py`.
- **Solución aplicada:** Se unificó en una única definición coherente heredando de `BaseDAO[UsuarioModelo, UUID]` e implementando `UsuarioDAOMemoria`.

---

## 6. Convención de Nombrado y Organización de Código

- **Idioma en DAOs y Dominio:** Todos los métodos de los DAOs deben utilizar nombres completos y descriptivos en **Español** (`obtener_por_id`, `obtener_todos`, `guardar`, `actualizar`, `eliminar`, `existe`).
- **Prohibición de abreviaciones no estándar:**
  - ❌ `vali_transicion` ➔ ✅ `validar_transicion`
  - ❌ `obt_estados` ➔ ✅ `obtener_estados`
  - ❌ `act_configuracion` ➔ ✅ `actualizar_configuracion`
  - ❌ `obt_configuracion` ➔ ✅ `obtener_configuracion`
  - ❌ `_vali_fechas` ➔ ✅ `_validar_fechas`
- **Docstrings obligatorios:** Todos los métodos de servicios de negocio y esquemas de entrada de FastAPI deben contar con docstrings completos indicando parámetros (`Args:`), retornos (`Returns:`) y excepciones (`Raises:`).

