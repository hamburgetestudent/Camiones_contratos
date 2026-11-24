# Modelado de MansoViaje

## Índice de diagramas UML

| Diagrama | Nota de lectura | Fuente editable |
| --- | --- | --- |
| 1. Casos de uso | [Actores, alcance y verificación KYC](modelados/1-casos-de-uso.md) · [PDF](modelados/1-casos-de-uso.pdf) | [draw.io](modelados/1-casos-de-uso.drawio) |
| 2. Clases | [Relaciones y multiplicidades del dominio](modelados/justificacion_diag_clases.md) | [XML de draw.io](modelados/diagrama_clases.xml) |
| 3. Secuencia | [Crear contrato en borrador](modelados/3-secuencia.md) | [draw.io](modelados/3-secuencia.drawio) |
| 4. Componentes | [Interfaces y responsabilidades](modelados/4-componentes.md) | [draw.io](modelados/4-componentes.drawio) |

## Nota de lectura

Para seguir un contrato por los cuatro diagramas, empiecen por el dador de carga y el caso **Crear contrato en borrador**. El diagrama de clases identifica el perfil tributario del dador y la entidad `ContratoModelo`. El de secuencia muestra en qué momento se comprueba la aprobación del perfil y por qué un rechazo impide guardar el contrato. En el de componentes se puede seguir ese mismo recorrido desde la API de contratos hasta los servicios y SQLite.
