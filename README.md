# Taller-Programacion
Este proyecto consiste en una plataforma integral multiplataforma (escritorio y web) orientada a la centralización y digitalización de contratos de transporte terrestre de carga. La solución funciona como un punto de encuentro entre empresas generadoras de carga y transportistas independientes o flotas de camioneros, optimizando el proceso de publicación, postulación, adjudicación y seguimiento de servicios de flete.

La arquitectura del sistema está estructurada mediante una separación clara de responsabilidades:

* **Frontend:** Desarrollado con **Electron** y **TypeScript**, proporciona una interfaz de usuario de escritorio multiplataforma, segura, altamente tipada y responsiva, garantizando una experiencia fluida e intuitiva para la gestión de contratos en tiempo real.
* **Backend:** Construido sobre **Python** utilizando **FastAPI**, actúa como una API REST de alto rendimiento y ejecución asíncrona. Se encarga de la lógica de negocio, la validación estricta de datos, la gestión del ciclo de vida de los acuerdos comerciales y la comunicación eficiente con la capa de presentación.

---

Cronologias de cambios, informes y cambios sustanciales : https://docs.google.com/document/d/1p95pKZ2zpQuFnw19-MtfZ5WIhdKAEz30nYLUg9G9B-U/edit?tab=t.0

---

## Requisitos del Sistema

Para el despliegue local en entorno de desarrollo se requiere:

* **Node.js**:  POR DEFINIR 
* **npm**: POR DEFINIR
* **Python**: v3.14.0 o superior

---

## Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/tu-repositorio.git
cd tu-repositorio
```

### 2. Configuración del Backend (FastAPI)
```bash
cd backend
python -m venv venv

# Activación del entorno virtual
# En Linux/macOS:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
> La documentación interactiva de la API estará disponible en `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`.

### 3. Configuración del Frontend (Electron)
```bash
cd ../frontend
npm install
npm run dev
```

## Arquitectura del sistema

- **Frontend:** Desarrollado con **Electron** y **TypeScript**...
- **Backend:** Construido sobre **Python** utilizando **FastAPI**...

### Diagrama de arquitectura

```mermaid
flowchart TD
    A[Usuario] --> B[Frontend<br/>Electron + TypeScript]
    B --> C[Backend<br/>Python + FastAPI]
    C --> D[principal.py]
    D --> E[modelos.py<br/>(Contratos y Validaciones)]
    D --> F[Almacenamiento temporal<br/>dict de contratos]
