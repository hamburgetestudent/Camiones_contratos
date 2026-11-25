# Revisión de dependencia externa: email-validator

## Registro

| Campo | Valor |
|---|---|
| Nombre | `email-validator` |
| Versión empleada | **2.3.0** (instalada en `.venv`; `requirements.txt` exige `>=2.2.0,<3`) |
| Enlaces de respaldo | PyPI: https://pypi.org/project/email-validator/ · Repositorio: https://github.com/JoshData/python-email-validator · Licencia: https://github.com/JoshData/python-email-validator/blob/main/LICENSE |

## 1. Utilidad y mantenimiento

- **Necesidad que resuelve:** validar la sintaxis de correos según las reglas reales (RFC 5321/5322 y IDNA), con mensajes de error claros.
- **Dónde se usa:** [domain/modelos_usuario.py](../domain/modelos_usuario.py), validador `UsuarioBase._validar_email`. Lo hereda `UsuarioCrear` (registro de usuarios). Antes el campo usaba la regex `^[\w\.-]+@[\w\.-]+\.\w+$`, que aceptaba `a..b@x.cl` o `.a@x.cl`. Además es la librería que Pydantic exige para `EmailStr`, por lo que ya viajaba en `requirements.txt` sin ser usada directamente.
- **Evidencia de mantenimiento (enlaces abiertos y verificados el 2026-11-24):**
  - PyPI muestra como última versión la **2.4.0**, publicada el **2026-11-14** (requiere Python 3.10+). La versión instalada en el proyecto es la 2.3.0 (2025-08-26); el rango `>=2.2.0,<3` permite actualizar a la 2.4.0.
  - El repositorio oficial tiene un commit en `main` de hace 2 días (*"Set mx to None when the deliverability check cannot be completed (#200)"*) y el `CHANGELOG.md` incluye la 2.4.0. La pestaña *Releases* de GitHub llega solo hasta v2.3.0; la 2.4.0 figura en PyPI y en el CHANGELOG pero no tiene release creado allí.
  - Hay issues abiertos y recientes (11 abiertos; p. ej. #164 de dic. 2025), lo que muestra que el proyecto recibe reportes y sigue activo.
  - Es la dependencia que Pydantic exige para `EmailStr`, por lo que su soporte está ligado al de FastAPI/Pydantic.
  - La versión 2.1.0 fue retirada (*yanked*) en PyPI: *"Forgot to drop Python 3.7 from python_requires"* (https://github.com/JoshData/python-email-validator/pull/118); se reemplazó al día siguiente. Por eso el mínimo del proyecto es `2.2.0`.

## 2. Licencia o condiciones

- **Licencia:** The Unlicense (dominio público), confirmada en los metadatos del paquete instalado (`Classifier: License :: OSI Approved :: The Unlicense`).
- **Obligación aplicable:** no impone atribución ni copyleft; la obligación práctica es **no ocultar la dependencia**: mantenerla declarada y versionada en `requirements.txt` para que la compatibilidad de licencias sea auditable.

## 3. Riesgo y mitigación

- **Riesgo concreto:** una actualización de `email-validator` cambia las reglas de validación y deja de aceptar correos de usuarios reales o rompe el registro.
  - **Probabilidad: media** (estimación inicial "baja-media", confirmada con el CHANGELOG). Las 11 versiones del CHANGELOG que alteran qué correos se aceptan o rechazan van de 1.0.0 (2015) a 2.4.0 (2026): unas 2 por año desde 2022 (1.2.0 a 2.4.0, 9 cambios en ~4,6 años), frente a unos 0,5 por año antes. Ejemplos: la 1.2.0 rechaza dominios de uso especial y la 2.0.0 deja de aceptar por defecto direcciones con comillas y dominios literales. Hubo regresiones reales: la 1.3.0 endureció la comprobación SPF y la 1.3.1 la relajó cuatro meses después, y el issue #160 (sep. 2025) reporta que la 2.3 rompió reglas de modelos Pydantic.
  - **Por qué no es alta:** la mayoría de los endurecimientos afectan casos borde (Unicode inseguro, IPv6 con zona, regla Bidi de IDNA, dominios muy largos), y la 2.3.0 incluso *relajó* una regla (el límite de 64 caracteres de la parte local).
  - **Impacto:** alto (nadie podría registrarse ni crear usuarios).
- **Medida de mitigación:** (a) se llama con `check_deliverability=False`, para que el registro no dependa de consultas DNS ni de red; (b) pruebas automáticas que fijan el comportamiento esperado; (c) **aplicado:** `requirements.txt` ahora declara `email-validator>=2.2.0,<3`: excluye la 2.1.0 retirada y bloquea saltos a una versión mayor sin revisión.
- **Cómo se comprueba:**
  1. `PYTHONPATH=. python scripts/ejemplo_email_validator.py` imprime la versión y el resultado para casos válidos e inválidos.
  2. `python -m unittest tests.usuarios.test_dependencia_email_validator` verifica versión mayor ≥ 2, que `requirements.txt` contenga el rango acotado, aceptación de un correo válido y rechazo de `ana@@empresa.cl`, `ana@empresa`, correos con espacios y puntos consecutivos.
  3. Suite completa (`python -m unittest discover -s tests -t .`): 216 pruebas OK tras el cambio. Si una actualización rompe las reglas, estos tests fallan en CI.

## Cómo ejecutar el test

Desde la raíz del proyecto, con el entorno virtual activo:

```bash
python -m unittest tests.usuarios.test_dependencia_email_validator -v
```

Resultado esperado: `Ran 4 tests ... OK` (versión fijada, rango acotado en `requirements.txt`, correo válido aceptado y formatos inválidos rechazados).

Con `pytest` (como en el CI):

```bash
python -m pytest tests/usuarios/test_dependencia_email_validator.py -v
```

## Ejemplo ejecutable

[scripts/ejemplo_email_validator.py](../scripts/ejemplo_email_validator.py) construye `UsuarioBase` con distintos correos y muestra cuáles acepta o rechaza.

## Cambios realizados

- `domain/modelos_usuario.py`: se reemplaza el `pattern` regex de `email` por un `field_validator` que usa `email_validator.validate_email`. El valor se conserva tal cual (no se normaliza), así el comportamiento con mayúsculas no cambia.
- `scripts/ejemplo_email_validator.py`: ejemplo ejecutable (nuevo).
- `tests/usuarios/test_dependencia_email_validator.py`: pruebas de integración (nuevo).
- `requirements.txt`: rango `>=2.2.0,<3`.
- `docs/revision-dependencia-email-validator.md`: este documento.

## Fuentes consultadas

- Verificación de enlaces y análisis del CHANGELOG (2026-11-24, hecha por un agente con acceso web):
  - https://pypi.org/project/email-validator/
  - https://github.com/JoshData/python-email-validator
  - https://github.com/JoshData/python-email-validator/releases
  - https://github.com/JoshData/python-email-validator/blob/main/LICENSE (texto de The Unlicense)
  - https://github.com/JoshData/python-email-validator/issues (incluye #160)
  - https://github.com/JoshData/python-email-validator/blob/main/CHANGELOG.md
- Fuentes complementarias:
  - PyPI (espejo CERN): https://simple-repository.app.cern.ch/project/email-validator
  - PiWheels: https://www.piwheels.org/project/email-validator/
  - Notas de release 2.3.0: https://newreleases.io/project/pypi/email-validator/release/2.3.0
  - PyPI 2.1.0 (retirada): https://pypi.org/project/email-validator/2.1.0
- Licencia confirmada además en el archivo LICENSE del repositorio y en los metadatos locales del paquete instalado.

Componente propio relacionado: [contrato-usuario-service.md](contrato-usuario-service.md) (el registro de usuarios usa esta dependencia).
