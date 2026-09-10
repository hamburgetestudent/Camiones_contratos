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

* **Node.js**: v20.x (LTS) o superior
* **npm**: v10.x o superior
* **Python**: v3.10.0 o superior
* **fastapi**: ~0.109.0
* **uvicorn**: ~0.27.0
* **pydantic**: ~2.6.0

---

## Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone https://github.com/hamburgetestudent/Camiones_contratos.git
cd Camiones_contratos
```

### 2. Configuración del Backend (FastAPI)
```bash
python -m venv venv

# Activación del entorno virtual
# En Linux/macOS:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
> La documentación interactiva de la API estará disponible en `http://127.0.0.1:8000/docs`.

### 3. Configuración del Frontend (Electron)
```bash
cd frontend
npm install
npm run dev
```

### 4. Pruebas Automatizadas (Pytest)
```bash
pip install -r requirements-dev.txt
pytest -v
```

---

## Verificación post-instalación

Para confirmar que el servidor y la base de datos están funcionando correctamente, sigue los siguientes pasos:

1. **Verificación del Servidor HTTP (FastAPI):**
   - Inicia la aplicación ejecutando `uvicorn main:app --reload --host 127.0.0.1 --port 8000`.
   - Abre tu navegador en `http://127.0.0.1:8000/docs` para acceder a la documentación interactiva OpenAPI (Swagger UI).
   - Confirma que la interfaz liste correctamente todos los routers cargados (`/auth`, `/configuracion`, `/contratos`, `/onboarding`, `/subastas`).

2. **Verificación de Endpoints y Base de Datos:**
   - Realiza una petición GET al endpoint `http://127.0.0.1:8000/configuracion`. Deberías recibir una respuesta con código HTTP 200 OK y el cuerpo JSON correspondiente a las reglas de negocio globales.
   - Asegúrate de que las variables de entorno estén definidas en `.env` (copiado de `.env.example`). En caso de utilizar una base de datos PostgreSQL, verifica la conectividad con las credenciales indicadas en `DATABASE_URL`.

3. **Verificación de la Suite de Pruebas:**
   - Ejecuta `pytest -v` en la terminal para asegurarte de que todas las pruebas unitarias y de integración se ejecuten correctamente sin errores.

---

## Arquitectura del sistema

La arquitectura del sistema está estructurada mediante una separación clara de responsabilidades:

- **Frontend:** Desarrollado con **Electron** y **TypeScript**, proporciona la interfaz de usuario de escritorio.
- **Backend:** Construido con **Python** y **FastAPI**, se encarga de los endpoints, la lógica de negocio y la validación de los contratos.
- **Autenticación:** Gestión de registro y login modular desacoplado (`routers/login_router.py`, `services/login_service.py`, `domain/modelos_login.py`) conectado al validador del sistema de usuarios.
- **Modelos:** El archivo `modelos.py` contiene la estructura de los contratos y sus validaciones.
- **Almacenamiento:** Actualmente los contratos se almacenan temporalmente en un diccionario de Python, utilizado como almacenamiento en memoria.

### Diagrama de arquitectura

```mermaid
flowchart TD
    A[Usuario] --> B["Frontend<br/>Electron + TypeScript"]
    B --> C["Backend<br/>Python + FastAPI"]
    C --> D["main.py"]
    D --> E["modelos.py<br/>Contratos y Validaciones"]
    D --> F["Almacenamiento temporal<br/>dict de contratos"]
```
