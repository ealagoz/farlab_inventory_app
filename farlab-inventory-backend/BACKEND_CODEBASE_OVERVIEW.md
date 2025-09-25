# Codebase Overview

This document provides a technical overview of the FARLAB Inventory backend API, focusing on its architecture and the roles of its key directories.

## Project Structure

The project follows a clean, layered architecture that separates concerns into distinct modules:

```
/
├── main.py           # Main application entry point, middleware, and startup logic.
├── database.py       # Database engine, session management, and table creation.
├── models/           # SQLAlchemy ORM models (defines database tables).
├── schemas/          # Pydantic models (defines API data shapes/contracts).
├── routers/          # API endpoint definitions, grouped by resource.
└── utils/            # Utility functions, including auth dependencies.
```

## Layered Architecture

-   **Router Layer (`routers/`):** The entry point for all API requests. This layer handles HTTP requests, validates input, and returns responses.
-   **Schema Layer (`schemas/`):** Defines the "shape" of the data using Pydantic models, ensuring that data sent to and from the API is valid and structured correctly.
-   **Model/Data Access Layer (`models/`, `database.py`):** Defines the database structure through SQLAlchemy models and handles all direct interaction with the database.

## Database & ORM

-   **Connection:** The `database.py` file reads the `DATABASE_URL` from a `.env` file and creates a SQLAlchemy engine.
-   **Session Management:** A `get_db` dependency function injects a database session into each API endpoint that needs one, ensuring that each request gets its own session and that the session is always closed afterward.

## API & Routing

-   **Modular Routers:** The API is organized into modules within the `routers/` directory. Each module uses `fastapi.APIRouter` to create a mini-application, which is then included in the main `app` instance in `main.py`.
-   **Dependency Injection:** FastAPI's dependency injection system is used heavily to inject dependencies like the database session (`get_db`) and the current authenticated user (`get_current_user`).

## Authentication & Authorization

-   **Token-Based Auth:** The system uses JWTs for authentication. A user logs in via the `/api/token` endpoint and receives an access token.
-   **Dependencies for Security:** The `utils/dependencies.py` file contains dependencies that decode and validate the JWT, and fetch the corresponding user from the database.
