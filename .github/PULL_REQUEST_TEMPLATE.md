# Plantilla de Pull Request (PR)

## 📌 Descripción del Cambio
<!-- Describe de forma clara y concisa qué problema resuelve este Pull Request o qué funcionalidad incorpora. -->

Closes #(número de issue si aplica)

---

## 🛠️ Tipo de Cambio
<!-- Marca con una 'x' las casillas que apliquen -->
- [ ] 🐛 **Bugfix** (corrección de un error sin romper funcionalidad previa)
- [ ] ✨ **Feature** (nueva funcionalidad añadida)
- [ ] ♻️ **Refactor** (mejora en estructura, legibilidad o nombrado sin cambio funcional)
- [ ] 📝 **Documentación** (actualización de README, CONTRIBUTING, docstrings, etc.)
- [ ] ⚙️ **Configuración / Tooling** (ajustes en linter, dependencias, CI/CD)

---

## 🎯 Criterios de Evaluación Impactados
<!-- Selecciona los criterios de evaluación cubiertos en esta entrega -->
- [ ] **E1:** Modelado de Dominio y Máquina de Estados
- [ ] **E2:** Arquitectura y Flujo de Contratos
- [ ] **E3:** Historial y Buenas Prácticas de Git
- [ ] **E4:** Calidad de Código, Linting y Documentación Backend
- [ ] **E5:** Integración de Servicios y Pruebas

---

## 🔍 Corrección Destacada por Análisis Estático (Ruff)
<!-- En cumplimiento con el Criterio 5 / E4: Documenta al menos un bug o mejora detectado gracias al linter -->
* **Regla de Ruff detectada:** `[Ej: F821 / F401 / I001 / UP006]`
* **Archivo afectado:** `[Ej: domain/modelos.py]`
* **Problema identificado:** <!-- Explica el fallo en tiempo de ejecución o advertencia -->
* **Solución aplicada:** <!-- Explica cómo se corrigió -->

---

## ✅ Checklist de Calidad
<!-- Asegúrate de marcar todas las casillas antes de solicitar revisión -->
- [ ] Mi código sigue la convención de estilo del proyecto documentada en `CONTRIBUTING.md`.
- [ ] He ejecutado localmente `ruff check .` y no arroja advertencias ni errores.
- [ ] He ejecutado `ruff format .` para formatear el código de manera consistente.
- [ ] Todos los métodos y endpoints nuevos o modificados cuentan con docstrings completos (`Args`, `Returns`, `Raises`).
- [ ] Se han eliminado abreviaciones no estándar (`vali_`, `obt_`, `act_`) a favor de nombres claros en español.
- [ ] Mis cambios no introducen advertencias ni rompen pruebas existentes.

---

## 🧪 Pasos para Verificación / Pruebas
<!-- Indica los comandos necesarios para probar o verificar los cambios de este PR -->
```bash
# 1. Comprobar que el linter pase limpiamente
ruff check .

# 2. Comprobar formato
ruff format --check .

# 3. Ejecutar pruebas unitarias (cuando aplique)
pytest
```

