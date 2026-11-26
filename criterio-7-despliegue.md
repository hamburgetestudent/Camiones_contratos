# Entrega de MansoViaje 1.0.0 para Windows x64

**ISF224 · Hito 3 · Criterio 7: empaquetado y documentación de cierre**  
**Fecha de entrega:** 25 de noviembre de 2026

Entregamos MansoViaje como un instalador de escritorio para Windows x64. Quien evalúa el proyecto puede descargar un archivo, instalarlo con su cuenta de Windows y abrir la aplicación desde Inicio. El instalador incluye la interfaz, el servidor y los datos de demostración necesarios para publicar una carga, recibir una oferta y consultarla después de cerrar y volver a abrir el programa.

**Estado del criterio 7:** el paquete está publicado, la versión está identificada y el equipo probó el ejecutable instalado. Queda pendiente que una persona de **otro equipo** repita el recorrido siguiendo únicamente el README y registre su resultado.

**Acceso a la entrega:** [Descargar MansoViaje 1.0.0](https://github.com/hamburgetestudent/Camiones_contratos/releases/tag/v1.0.0) · [Leer el README de esa versión](https://github.com/hamburgetestudent/Camiones_contratos/blob/v1.0.0/README.md) · [Consultar el acta de aceptación](aceptacion-escritorio-1.0.0.md)

## 1. Qué se evalua

| Requisito del criterio 7 | Qué entregamos | Evidencia |
|---|---|---|
| Paquete identificable y reproducible | Instalador `MansoViaje-1.0.0-win-x64.exe`, etiqueta `v1.0.0`, commit de construcción `37c73ac` y suma SHA-256 para identificar el archivo exacto. | [Publicación y descarga](https://github.com/hamburgetestudent/Camiones_contratos/releases/tag/v1.0.0) · [Commit de construcción](https://github.com/hamburgetestudent/Camiones_contratos/commit/37c73acdaeecd7a4268d546a07dce3401ba212af) |
| Versión y notas coherentes | Las notas identifican la versión, la fecha, los cambios, la compatibilidad, el tratamiento de los datos al actualizar y las limitaciones conocidas. | [Notas de la versión 1.0.0](https://github.com/hamburgetestudent/Camiones_contratos/blob/v1.0.0/CHANGELOG.md) |
| Instrucciones para instalar, ejecutar y extender | El README explica cómo verificar el instalador, iniciar la aplicación, completar una postulación, resolver problemas frecuentes y probar un cambio sobre las fuentes incluidas. | [README de la versión distribuida](https://github.com/hamburgetestudent/Camiones_contratos/blob/v1.0.0/README.md) |
| Informe de decisiones, resultados y pendientes | Registramos por qué elegimos el instalador, qué problema apareció al construirlo, cómo lo corregimos y qué ocurrió al probar la aplicación instalada. | [Acta de aceptación interna](aceptacion-escritorio-1.0.0.md) |
| Ejecución por otro equipo en un entorno limpio | La ficha está preparada para registrar el archivo recibido, la instalación, el flujo, el punto de extensión y las dificultades. **Pendiente de ejecución externa.** | [Ficha de revisión por otro equipo](revision-externa.md) |

## 2. Por qué elegimos un instalador de escritorio

MansoViaje tiene tres piezas que deben funcionar juntas. **Electron** muestra las pantallas del dador y del transportista. **FastAPI** recibe sus solicitudes y aplica las reglas del negocio. **SQLite** conserva los contratos y las ofertas.

Durante el desarrollo era necesario preparar Python y Node.js, instalar dependencias e iniciar los procesos. Elegimos reunir las tres piezas en un instalador porque el docente necesita evaluar el flujo del producto desde las mismas pantallas que usaría una persona. Con la aplicación instalada, Electron inicia su propio servidor y el usuario puede trabajar localmente sin preparar herramientas de desarrollo. GitHub se utiliza para distribuir el archivo; la operación cotidiana y los datos quedan en el equipo donde se instala.

Esta decisión tiene límites concretos. La distribución corresponde a **Windows x64**, requiere permiso de escritura en el perfil del usuario y necesita libre el puerto local **8000**. Cada perfil conserva su propia base de datos. El instalador académico carece de firma comercial, por lo que documentamos cómo comprobar su integridad antes de abrirlo.

## 3. Cómo pasamos del código al archivo entregado

1. **Identificamos las fuentes.** La etiqueta `v1.0.0` apunta al commit `37c73ac`. Elegimos `1.0.0` porque es la primera distribución integrada de escritorio en la que verificamos el recorrido completo, desde publicar una carga hasta recuperar la oferta después de reiniciar. La API también identifica el producto como `1.0.0`.
2. **Empaquetamos el servidor.** PyInstaller reunió el intérprete de Python, FastAPI, Uvicorn y el esquema de la base de datos. Así, el servidor puede iniciarse en el equipo del usuario aunque este no haya instalado Python.
3. **Construimos el instalador.** Compilamos la interfaz de Electron. Luego `electron-builder` incorporó el servidor y la documentación, y NSIS generó `MansoViaje-1.0.0-win-x64.exe`. En `resources/entrega/` se incluyen `VERSION.txt`, las fuentes en `fuentes.zip`, la configuración de ejemplo y los avisos de licencias.
4. **Identificamos el archivo probado.** Calculamos la suma SHA-256 y la comparamos con la del instalador descargado. El valor registrado en el acta es `EB985FDB0D72057197AA4C60888FCB6BBA9ECB82DCC0C7FBF4D8B49258693E63`. Esto permite que el docente y el equipo revisor comprueben que recibieron el mismo archivo que se instaló durante la aceptación.

[Script de construcción de la versión entregada](https://github.com/hamburgetestudent/Camiones_contratos/blob/v1.0.0/scripts/construir-entrega.ps1) · [Configuración del instalador](https://github.com/hamburgetestudent/Camiones_contratos/blob/v1.0.0/frontend/electron-builder.yml)

## 4. Qué comprobamos con la aplicación instalada

Al abrir MansoViaje, Electron inicia el servidor y consulta `/health` en `127.0.0.1:8000`. Comprueba la identidad de esa instancia antes de mostrar el login. La base `camiones.db` se guarda en una carpeta escribible del usuario, separada de los archivos del programa. Al cerrar la aplicación, el servidor se detiene y libera el puerto. Al volver a abrirla con el mismo perfil, se recuperan los datos.

La aceptación interna se realizó en **Windows 10 Pro x64**, instalando el archivo en una carpeta nueva y usando un perfil nuevo. El equipo de prueba tenía herramientas de desarrollo para automatizar la verificación. La prueba operó sobre **el ejecutable instalado**, que inició su propio servidor empaquetado.

| Prueba | Resultado observado |
|---|---|
| **Una oferta inválida.** El transportista intentó ofertar 4.900 CLP. | El formulario indicó el mínimo de 5.000 CLP. En una comprobación controlada del servidor, FastAPI también rechazó el importe con HTTP 422. La carga conservó sus datos y quedó sin ofertas. |
| **Una postulación completa.** El dador publicó una carga y el transportista ofertó 180.000 CLP. | La API respondió HTTP 201. El dador pudo consultar una oferta `POSTULADA` por 180.000 CLP y el contrato pasó a `EN_POSTULACION`. |
| **Reinicio y recuperación.** Cerramos la aplicación, ocupamos el puerto 8000 y volvimos a abrirla. | Electron informó que su servidor estaba indisponible. Al liberar el puerto y pulsar **Reintentar**, pudimos iniciar sesión y recuperar la misma oferta y el mismo estado del contrato. |

La suite del commit de entrega registró **229 pruebas y 76 subpruebas aprobadas**, con **93,4 % de cobertura** en las capas Python medidas. La prueba del instalador aportó una comprobación adicional: que Electron, el servidor empaquetado y la base local colaboran después de instalar el producto. [Acta con los resultados y los identificadores de prueba](aceptacion-escritorio-1.0.0.md) · [CI del commit entregado](https://github.com/hamburgetestudent/Camiones_contratos/actions/runs/45712407504)

## 5. Qué corregimos y cómo verificamos que el proyecto puede extenderse

**Corrección durante la construcción.** El primer intento desde una copia limpia se detuvo al recopilar los avisos de licencia de Chromium. Electron 44 descarga sus componentes de ejecución bajo demanda y el archivo requerido aún no estaba disponible. Ajustamos el script para completar esa descarga antes de reunir los avisos. Repetimos la construcción desde otra copia limpia y obtuvimos el instalador con los avisos incluidos.

**Extensión comprobada desde las fuentes entregadas.** Extraímos `fuentes.zip` y seguimos el ejemplo del README para ampliar el comentario de una oferta de 500 a 600 caracteres. El cambio requirió ajustar el límite en el formulario y en el modelo del servidor. La prueba aceptó 600 caracteres y rechazó 601. Este ensayo demuestra que una persona puede localizar el cambio y comprobarlo a partir del contenido distribuido. El instalador publicado conserva el límite original de 500 caracteres. [Ejemplo de extensión en el README](https://github.com/hamburgetestudent/Camiones_contratos/blob/v1.0.0/README.md#extender-el-comentario-de-una-oferta-y-probarlo)

## 6. Qué falta para cerrar el criterio 7

La tarea pendiente es la **revisión independiente del paquete**. Una persona de otro equipo debe descargar el instalador publicado, verificar su SHA-256 y seguir únicamente el README. La comprobación termina cuando esa persona puede abrir MansoViaje, completar la postulación, recuperar la oferta después de reiniciar y señalar dónde haría la extensión descrita.

La ficha debe registrar quién realizó la prueba, qué versión recibió, qué resultado obtuvo y en qué paso necesitó ayuda. Si una instrucción resulta insuficiente, corresponde corregirla y repetir el paso afectado. Hasta contar con ese registro, la evidencia disponible acredita la **aceptación interna** y la revisión externa permanece **pendiente**. [Completar la ficha de revisión externa](revision-externa.md)
