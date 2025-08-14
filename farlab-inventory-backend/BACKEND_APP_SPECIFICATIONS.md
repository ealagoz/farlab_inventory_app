# FarLab Inventory Backend Specifications

## 1. Introduction

This document provides a comprehensive overview of the FarLab Inventory Backend
application. This application is a RESTful API built with Python and FastAPI,
designed to manage laboratory inventory, including instruments, parts, and user
access. It features a robust authentication system, data validation, and a modular
structure for easy maintenance and scalability.

## 2. Technology Stack

The application is built using the following technologies:

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Web Server**: [Uvicorn](https://www.uvicorn.org/)
- **Database ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Database**: [PostgreSQL](https://www.postgresql.org/) (`psycopg2-binary`)
- **Authentication**: JWT with `python-jose`, `passlib`, and `bcrypt` for password hashing.
- **Data Validation**: [Pydantic](https://pydantic-docs.helpmanual.io/)
- **Configuration**: `python-dotenv` and `pydantic-settings`
- **Dependency Management & Virtual Environment**: `pip` with `requirements.txt` and [pyenv](https://github.com/pyenv/pyenv) for Python version management.

## 3. Project Structure

The project is organized into the following directories and files:
```
/
├── APP_SPECIFICATIONS.md
├── BACKEND_CODEBASE_OVERVIEW.md
├── README.md
├── **init**.py
├── database.py
├── farlab_inventory.log
├── main.py
├── models
│   ├── **init**.py
│   ├── alert.py
│   ├── base.py
│   ├── instrument.py
│   ├── instrument_part.py
│   ├── part.py
│   └── user.py
├── requirements.txt
├── routers
│   ├── **init**.py
│   ├── alerts.py
│   ├── auth.py
│   ├── instruments.py
│   ├── parts.py
│   └── users.py
├── schemas
│   ├── **init**.py
│   ├── alert.py
│   ├── common.py
│   ├── instrument.py
│   ├── instrument_part.py
│   ├── part.py
│   ├── token.py
│   └── user.py
├── scripts
│   └── create_admin.py
├── services
│   ├── **init**.py
│   ├── alert_service.py
│   ├── auth_service.py
│   ├── notification_service.py
│   └── scheduler.py
└── utils
├── **init**.py
├── config.py
├── dependencies.py
├── logging_config.py
├── security.py
└── validators.py
```

## 4. Core Features

The application provides the following core features:

- **User Management**: Create, retrieve, update, and delete users.
- **Authentication**: Secure user login and registration with JWT-based authentication.
- **Instrument Management**: Manage laboratory instruments, including their parts and specifications.
- **Part Management**: Track individual parts, their stock levels, and associations with instruments.
- **Alerting System**: A system for creating and managing alerts, likely related to inventory levels or instrument status.
- **Scheduled Tasks**: The `scheduler.py` service suggests the ability to run background tasks at specified intervals.

## 5. API Endpoints

The API is organized into the following routers:

- **`/auth`**: Handles user authentication, including login and token generation.
- **`/users`**: Provides CRUD operations for user management.
- **`/instruments`**: Provides CRUD operations for managing instruments.
- **`/parts`**: Provides CRUD operations for managing parts.
- **`/alerts`**: Provides CRUD operations for the alerting system.

_A more detailed API documentation could be generated automatically by FastAPI and linked here._

## 6. Database Schema

The database schema is defined using SQLAlchemy models in the `models/` directory. The key models are:

- **`User`**: Stores user information, including credentials.
- **`Instrument`**: Represents a laboratory instrument.
- **`Part`**: Represents a part that can be used in an instrument.
- **`InstrumentPart`**: A many-to-many relationship table between instruments and parts.
- **`Alert`**: Stores information about alerts.

## 7. Authentication

Authentication is handled using JSON Web Tokens (JWT). The process is as follows:

1. A user submits their credentials to the `/auth/token` endpoint.
2. The `auth_service` verifies the credentials.
3. If the credentials are valid, a JWT is generated and returned to the user.
4. The user must include this JWT in the `Authorization` header of subsequent requests to protected endpoints.
5. A FastAPI dependency (`get_current_user`) verifies the JWT and retrieves the current user for each request.

## 8. Configuration

Application configuration is managed through environment variables, loaded from a `.env` file using `python-dotenv` and `pydantic-settings`. Key configuration variables likely include:

- `DATABASE_URL`: The connection string for the PostgreSQL database.
- `SECRET_KEY`: A secret key for signing JWTs.
- `ALGORITHM`: The algorithm used for JWT signing (e.g., `HS256`).
- `ACCESS_TOKEN_EXPIRE_MINUTES`: The expiration time for access tokens.

## 9. Running the Application

To run the application locally, follow these steps:

1. **Set up Python Environment**:
   This project uses `pyenv` to manage the Python version.

   - Install the Python version specified in `.python-version` (e.g., `pyenv install`).
   - Create a virtual environment (e.g., `pyenv virtualenv <python-version> farlab-inventory-backend`).
   - Activate the environment (e.g., `pyenv local farlab-inventory-backend`).

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables**:
   Create a `.env` file in the root directory and add the necessary configuration variables.

4. **Run the Development Server**:
   ```bash
   uvicorn main:app --reload
   ```

The application will be available at `http://127.0.0.1:8000`.

## 10. Future Improvements

- **Add API Documentation**: Link to the auto-generated FastAPI documentation (e.g., `/docs`).
- **Containerization**: For more robust deployment and environment isolation, consider adding a `Dockerfile` to containerize the application with Docker.
- **Testing**: Implement a comprehensive test suite to ensure code quality and prevent regressions.
