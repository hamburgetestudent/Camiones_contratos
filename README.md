# Taller-Programacion
Este proyecto consiste en una plataforma integral multiplataforma (escritorio y web) orientada a la centralización y digitalización de contratos de transporte terrestre de carga. La solución funciona como un punto de encuentro entre empresas generadoras de carga y transportistas independientes o flotas de camioneros, optimizando el proceso de publicación, postulación, adjudicación y seguimiento de servicios de flete.

La arquitectura del sistema está estructurada mediante una separación clara de responsabilidades:

- **Frontend:** Desarrollado con **Electron** y **TypeScript**, proporciona una interfaz de usuario de escritorio multiplataforma, segura, altamente tipada y responsiva, garantizando una experiencia fluida e intuitiva para la gestión de contratos en tiempo real.
- **Backend:** Construido sobre **Python** utilizando **FastAPI**, actúa como una API REST de alto rendimiento y ejecución asíncrona. Se encarga de la lógica de negocio, la validación estricta de datos, la gestión del ciclo de vida de los acuerdos comerciales y la comunicación eficiente con la capa de presentación.

---

Cronologias de cambios, informes y cambios sustanciales : https://docs.google.com/document/d/1p95pKZ2zpQuFnw19-MtfZ5WIhdKAEz30nYLUg9G9B-U/edit?tab=t.0

---

## Requisitos del Sistema

Para el despliegue local en entorno de desarrollo se requiere:

- **Node.js**: v20.x (LTS) o superior
- **npm**: v10.x o superior
- **Python**: v3.10.0 o superior
- **fastapi**: ~0.109.0
- **uvicorn**: ~0.27.0
- **pydantic**: ~2.6.0

---

## Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone [https://github.com/hamburgetestudent/Camiones_contratos.git](https://github.com/hamburgetestudent/Camiones_contratos.git)
cd Camiones_contratos