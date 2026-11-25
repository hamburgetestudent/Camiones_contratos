# Camiones Contratos — Copilot Instructions

## Build, run, and test

Run backend commands from the repository root (`Camiones_contratos/`).

### Backend

- Create/activate the documented Python virtual environment and install runtime dependencies with `pip install -r requirements.txt`.
- Start the FastAPI app with `uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000`. The OpenAPI UI is at `http://127.0.0.1:8000/docs`.
- Run the full Python test suite with `npm run test` (or `python run_tests.py`).
- Run Ruff linting with `npm run lint` (`ruff check .`) and formatting validation with `npm run format:py:check` (`ruff format --check .`). `npm run lint:fix` and `npm run format:py` apply safe fixes and formatting.

### Frontend

Run frontend commands from `frontend/`.

- Install dependencies with `npm install`.
- Compile TypeScript with `npm run build`.
- Run Electron after compiling with `npm start`.
- Run the TypeScript watcher with `npm run dev`.

The frontend TypeScript compiler is strict, targets ES2022/CommonJS, writes compiled files to `frontend/dist/`, and includes only `frontend/src/**/*.ts`.

## Architecture

This is a desktop Electron client backed by a modular FastAPI REST application.

- `backend/app/main.py` creates the FastAPI application and registers the authentication, configuration, contracts, onboarding, and auction routers.
- Each domain lives in `backend/app/modules/<domain>/` (`router.py`, `service.py`, `dao.py`, `models.py`). `router.py` is the HTTP boundary. Routers define Pydantic request/response schemas, translate domain/service failures to HTTP errors, and obtain services through typed dependencies in `backend/app/core/http.py`.
- `service.py` files contain application use cases. Contract, auction, onboarding, and user services orchestrate domain validation and persistence; `backend/app/core/dependencies.py` owns the shared service instances.
- `models.py` files contain Pydantic domain models and business rules. `MaquinaEstadosContrato` is the authoritative finite-state machine for contract lifecycle transitions; contract creation and state changes must go through these rules.
- `backend/app/db/` isolates SQLite persistence (`conexion.py`, `schema.sql`, `base_dao.py`).
- `frontend/electron/main.ts` creates the Electron window and loads `frontend/src/paginas/login/login.html`; TypeScript is compiled before Electron runs.

For setup details, consult [`README.md`](../README.md).

## Repository conventions

- Keep the dependency direction `router -> service -> models/DAO`; do not put business rules or direct persistence logic in routers.
- Use dependency injection for DAOs and services. Preserve the shared instances in `backend/app/core/dependencies.py` unless a change explicitly requires different application lifetime semantics.
- Treat `MaquinaEstadosContrato.TRANSICIONES_PERMITIDAS` as the single source of truth for legal contract transitions. Use `cambiar_estado` so transition invariants (publication timestamps and transport assignment) are enforced.
- Define and validate API payloads with Pydantic at the router/domain boundary. Models use strict field constraints and cross-field validators for dates, capacity, special cargo requirements, and financial totals.
- Use descriptive Spanish names for domain, DAO, service, and validation methods (`obtener_por_id`, `obtener_todos`, `guardar`, `actualizar`, `eliminar`, `validar_transicion`). Avoid introducing abbreviated names; existing aliases are retained only for backward compatibility.
- Service methods and FastAPI input schemas should have docstrings with `Args`, `Returns`, and `Raises` where applicable, following [`CONTRIBUTING.md`](../CONTRIBUTING.md).
- Follow the Ruff configuration in `pyproject.toml`: Python 3.12 target, 120-character lines, double quotes, and rule groups `E`, `F`, `W`, `I`, `N`, and `UP`.
- Keep frontend source in `frontend/src/` and static UI assets in `frontend/paginas/`; do not edit generated `frontend/dist/` output instead of the TypeScript source.
- Do not commit `.env` files, virtual environments, `node_modules/`, or generated caches; use `.env.example` for documenting environment variables.
