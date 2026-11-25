# Aceptación del instalador MansoViaje 1.0.0

El 25 de noviembre de 2026 se construyó y probó internamente el instalador **MansoViaje-1.0.0-win-x64.exe** (138.672.716 bytes). El instalador leído para calcular el hash fue el mismo ejecutado para la instalación y conservado para entrega.

| Identificación | Valor |
|---|---|
| Commit de construcción y de las fuentes dentro del instalador | [37c73acdaeecd7a4268d546a07dce3401ba212af](https://github.com/hamburgetestudent/Camiones_contratos/commit/37c73acdaeecd7a4268d546a07dce3401ba212af) |
| SHA-256 del instalador | `EB985FDB0D72057197AA4C60888FCB6BBA9ECB82DCC0C7FBF4D8B49258693E63` |
| Etiqueta correspondiente | `v1.0.0` |
| Entorno ensayado | Windows 10 Pro x64 22H2, compilación 19045. Construcción con Python 3.12.14, PyInstaller 6.22.3, Node 26.13.0, npm 11.20.0, Electron 44.0.0 y electron-builder 26.18.0. |
| Suite y cobertura local de ese commit | 229 pruebas y 76 subpruebas aprobadas, 93,4 % con ramas en los directorios declarados en [.coveragerc](../.coveragerc). El programa de escritorio se verifica por aceptación. |
| CI sobre ese commit | [Ejecución 45712407504 aprobada](https://github.com/hamburgetestudent/Camiones_contratos/actions/runs/45712407504) · [artefacto cobertura](https://github.com/hamburgetestudent/Camiones_contratos/actions/runs/45712407504/artifacts/15069045573) |

## Procedimiento y resultados

1. Desde una copia Git limpia del commit, ejecutar los dos comandos de reconstrucción del README. El primer ensayo había detectado que faltaba descargar el runtime de Electron para recopilar sus avisos. La segunda construcción, desde otra carpeta limpia, terminó con código 0 e incluyó el runtime, los avisos, el esquema, la configuración de ejemplo y el ZIP de fuentes.
2. Comprobar el SHA-256, instalar el archivo en una carpeta nueva mediante el comando silencioso del README y comprobar que `resources/entrega/VERSION.txt` identifica el commit indicado. El instalador terminó con código 0. Este equipo contenía herramientas de desarrollo para automatizar la prueba. El ejecutable inició su propio backend empaquetado.
3. Extraer las fuentes finales en otra carpeta, ejecutar `npm.cmd --prefix frontend ci` y lanzar [el guion de aceptación](../frontend/tests/entrega.e2e.cjs) apuntándolo al **ejecutable instalado**. El guion creó un perfil y una base nuevos. Usó el servidor real y la interfaz de Electron. Código de salida 0.

| Caso | Resultado esperado | Resultado obtenido |
|---|---|---|
| Datos inválidos. El transportista intenta ofertar 4.900 CLP. Para comprobar también la respuesta del servidor se retira el mínimo HTML únicamente en el formulario de prueba y se vuelve a enviar. | El formulario bloquea el primer envío. En el segundo, FastAPI responde 422 y Electron explica el límite. La carga conserva todos sus campos y sigue sin ofertas. | Se verificaron la restricción HTML, el 422, el aviso visible con el mínimo y la igualdad de los datos anteriores. |
| Datos válidos. Crear y publicar una carga como dador, entrar como transportista, enviar 180.000 CLP y revisar ofertas con la cuenta del dador. | HTTP 201, una oferta POSTULADA por 180.000 CLP, contrato EN_POSTULACION y lectura posterior en el panel del dador. | Contrato `6908f84d-7e08-48c6-ab0a-d85342344432`, oferta `25f88170-a4aa-4b16-8490-d5f9aaf29523`. La lectura posterior coincidió con el resultado del envío. |
| Recurso ausente. Tras cerrar, ocupar el puerto 8000 con un servidor de prueba que responde 503. Abrir MansoViaje, liberar el puerto y pulsar Reintentar. | La aplicación reconoce que su backend está indisponible, informa el error y recupera la conexión. Al reiniciar sesión se recuperan los datos. | Electron mostró el error. El reintento permitió leer la misma oferta y el mismo estado del contrato. Tras cerrar de nuevo se pudo reservar el puerto 8000. |

## Extensión y revisión independiente

En una copia extraída de las fuentes se amplió el límite de comentario del formulario y del modelo a 600 caracteres siguiendo el README. La prueba del módulo pasó cuatro casos, incluidos 600 admitidos y 601 rechazados. Se verificó también el arranque de desarrollo con `npm.cmd start`, el login visible, salud 200 y el cierre de ambos procesos. Esa modificación fue un ensayo en la copia extraída y la versión distribuida conserva el límite original de 500.

**Pendiente externo.** Otra persona debe descargar este instalador, seguir el README y completar [la ficha de revisión](revision-externa.md). Registrar la dificultad, el cambio y la repetición del paso si requiere corrección. La verificación interna se hizo con carpeta y perfil nuevos en la máquina de construcción. La ficha sigue pendiente hasta recibir evidencia real.
