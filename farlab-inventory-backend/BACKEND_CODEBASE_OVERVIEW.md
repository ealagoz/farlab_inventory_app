# FARLAB Inventory Backend: Codebase Overview

## 1. Project Overview

This document provides a technical overview of the FARLAB Inventory backend API. This application serves as
the central data and logic layer for the inventory management system, providing a RESTful API for the
frontend client to consume. It handles data storage, business logic, user authentication, and
authorization.

## 2. Core Technologies

- **Framework:** **FastAPI** is the core web framework used to build the API. It's chosen for its high
performance, automatic interactive documentation (Swagger UI & ReDoc), and its modern Python features.
- **Database ORM:** **SQLAlchemy** is used as the Object-Relational Mapper. It provides a powerful "unit
of work" pattern for database sessions and allows developers to interact with the database using Python
objects instead of raw SQL.
- **Database:** The database is **PostgreSQL**.
- **Database Migrations:** **Alembic** is included for handling database schema migrations, allowing for
version-controlled changes to the database structure over time.
- **Data Validation & Serialization:** **Pydantic** is used extensively for data validation,
serialization, and settings management. It's at the heart of FastAPI's data handling, ensuring that
incoming data matches predefined schemas and that outgoing data is formatted correctly.
- **Authentication:** Authentication is handled using **JWT (JSON Web Tokens)** and the **OAuth2**
standard (`OAuth2PasswordBearer`). `passlib` and `bcrypt` are used for securely hashing and verifying
passwords.
- **ASGI Server:** **Uvicorn** is the lightning-fast ASGI (Asynchronous Server Gateway Interface) server
used to run the application.

## 3. Project Structure & Architecture

The project follows a clean, layered architecture that separates concerns into distinct modules:
/
├── main.py # Main application entry point, middleware, and startup logic.
├── database.py # Database engine, session management, and table creation.
├── requirements.txt # Project dependencies.
├── models/ # SQLAlchemy ORM models (defines database tables).
├── schemas/ # Pydantic models (defines API data shapes/contracts).
├── routers/ # API endpoint definitions, grouped by resource.
└── utils/ # Utility functions, including auth dependencies.

**Layered Architecture:**
- **Router Layer (`routers/`):** This is the entry point for all API requests. Each file (e.g.,
`instruments.py`) groups related endpoints (e.g., `/api/instruments`). This layer is responsible for
handling HTTP requests, validating input, and returning responses. It's the "Controller" in an MVC pattern.
- **Schema Layer (`schemas/`):** This layer defines the "shape" of the data. Pydantic models here
ensure that data sent to an endpoint is valid and that data sent back to the client is structured
correctly. It separates the API data contract from the internal database model.
- **Model/Data Access Layer (`models/`, `database.py`):** This layer defines the database structure
through SQLAlchemy models. All direct interaction with the database (queries, commits, etc.) happens here,
abstracted away from the router layer.

## 4. Database & ORM

- **Connection:** The `database.py` file reads the `DATABASE_URL` from a `.env` file and creates a
SQLAlchemy engine.
- **Session Management:** It uses a `get_db` dependency function to inject a database session into each
API endpoint that needs one. This function ensures that each request gets its own session and that the
session is always closed afterward, which is a critical pattern for preventing connection leaks.
- **Models:** The `models/` directory contains Python classes that inherit from a declarative `Base`.
Each class maps to a table in the database (e.g., `Instrument`, `Part`, `User`). SQLAlchemy uses these
models to perform all database operations.

## 5. API & Routing

- **Modular Routers:** The API is organized into modules within the `routers/` directory. Each module
uses `fastapi.APIRouter` to create a mini-application, which is then included in the main `app` instance in
`main.py`. This keeps the main application file clean and organized.
- **Dependency Injection:** FastAPI's dependency injection system is used heavily. The `Depends()`
function is used to inject dependencies like the database session (`get_db`) and the current authenticated
user (`get_current_user`) into endpoint functions.

## 6. Authentication & Authorization

- **Token-Based Auth:** The system uses JWTs for authentication. A user logs in via the `/api/token`
endpoint and receives an access token. This token must be included in the `Authorization` header for all
protected endpoints.
- **Dependencies for Security:** The `utils/dependencies.py` file is crucial.
`get_current_user`: A dependency that decodes the JWT, validates it, and fetches the corresponding
user from the database. Any endpoint that requires a user to be logged in includes this dependency.
`get_current_admin_user`: A dependency that first gets the current user and then checks if they
have admin privileges, raising a `403 Forbidden` error if they do not. This provides a simple and reusable
way to protect admin-only endpoints.
