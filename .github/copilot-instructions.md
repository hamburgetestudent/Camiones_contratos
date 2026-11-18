# Camiones Contratos — Copilot Instructions

## Build, run, and test

Run backend commands from the repository root (`Camiones_contratos/`).

### Backend

- Create/activate the documented Python virtual environment and install runtime dependencies with `pip install -r requirements.txt`.
- Start the FastAPI app with `uvicorn main:app --reload --host 127.0.0.1 --port 8000`. The OpenAPI UI is at `http://127.0.0.1:8000/docs`.
- Install development tools with `pip install -r requirements-dev.txt`.
- Run the full Python test suite with `pytest -v`.
- Run the repository verification harness with `pytest inicio_test.py -v`. It checks Python compilation/importability and required frontend files.
- Run one verification test with, for example, `pytest inicio_test.py::TestCompilacionCodigo::test_compilacion_integral_sin_errores -v`. Use `pytest inicio_test.py -k <substring> -v` when selecting by name.
- Run Ruff linting with `ruff check .` and formatting validation with `ruff format --check .`. `ruff check --fix .` and `ruff format .` apply the project's safe fixes and formatting.

### Frontend

Run frontend commands from `frontend/`.

- Install dependencies with `npm install`.
- Compile TypeScript with `npm run build`.
- Run Electron after compiling with `npm start`.
- Run the TypeScript watcher with `npm run dev`.

The frontend TypeScript compiler is strict, targets ES2022/CommonJS, writes compiled files to `frontend/dist/`, and includes only `frontend/src/**/*.ts`.

## Architecture

This is a desktop Electron client backed by a modular FastAPI REST application.

- `main.py` creates the FastAPI application and registers the authentication, login, configuration, contracts, onboarding, and auction routers.
- `routers/` is the HTTP boundary. Routers define Pydantic request/response schemas, translate domain/service failures to HTTP errors, and obtain services through typed dependencies in `routers/comun.py`.
- `services/` contains application use cases. Contract and auction services orchestrate domain validation and persistence; `services/dependencies.py` owns the shared in-memory DAO/service instances.
- `domain/` contains Pydantic domain models and business rules. `MaquinaEstadosContrato` is the authoritative finite-state machine for contract lifecycle transitions; contract creation and state changes must go through these rules.
- `dao/` isolates persistence behind Spanish-named CRUD interfaces. Current implementations use thread-safe in-memory dictionaries, so data is process-local and is lost on restart.
- `frontend/src/main.ts` creates the Electron window and loads `frontend/paginas/index.html`; TypeScript is compiled before Electron runs.

For the fuller rationale and module boundaries, consult [`Arquitectura.md`](../Arquitectura.md). For setup details, consult [`README.md`](../README.md).

## Repository conventions

- Keep the dependency direction `routers -> services -> domain/DAO`; do not put business rules or direct persistence logic in routers.
- Use dependency injection for DAOs and services. Preserve the shared instances in `services/dependencies.py` unless a change explicitly requires different application lifetime semantics.
- Treat `MaquinaEstadosContrato.TRANSICIONES_PERMITIDAS` as the single source of truth for legal contract transitions. Use `cambiar_estado` so transition invariants (publication timestamps and transport assignment) are enforced.
- Define and validate API payloads with Pydantic at the router/domain boundary. Models use strict field constraints and cross-field validators for dates, capacity, special cargo requirements, and financial totals.
- Use descriptive Spanish names for domain, DAO, service, and validation methods (`obtener_por_id`, `obtener_todos`, `guardar`, `actualizar`, `eliminar`, `validar_transicion`). Avoid introducing abbreviated names; existing aliases are retained only for backward compatibility.
- Service methods and FastAPI input schemas should have docstrings with `Args`, `Returns`, and `Raises` where applicable, following [`CONTRIBUTING.md`](../CONTRIBUTING.md).
- Follow the Ruff configuration in `pyproject.toml`: Python 3.12 target, 120-character lines, double quotes, and rule groups `E`, `F`, `W`, `I`, `N`, and `UP`.
- Keep frontend source in `frontend/src/` and static UI assets in `frontend/paginas/`; do not edit generated `frontend/dist/` output instead of the TypeScript source.
- Do not commit `.env` files, virtual environments, `node_modules/`, or generated caches; use `.env.example` for documenting environment variables.
