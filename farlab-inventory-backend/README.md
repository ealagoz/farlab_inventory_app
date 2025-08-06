# FARLAB Inventory Management System - Backend

This repository contains the backend server for the FARLAB Inventory Management System. It is a robust, secure, and efficient API built with FastAPI that provides all the necessary endpoints to manage laboratory instruments, parts, users, and stock alerts.

---

## Table of Contents

- [Project Description](#project-description)
- [Architecture and Technology Stack](#architecture-and-technology-stack)
- [Project Layout](#project-layout)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Setup and Installation](#setup-and-installation)
- [Running the Server](#running-the-server)

---

## Project Description

The primary goal of this project is to provide a centralized system for tracking the inventory of critical laboratory parts. It allows lab members to see which parts are used by which instruments, monitor stock levels, and receive automated alerts when stock is running low. The system is designed to be accessed via a frontend application, and it includes role-based access control to distinguish between regular users and administrators.

## Architecture and Technology Stack

This project follows a modern, layered architecture pattern to ensure a clean separation of concerns.

- **Framework:** **FastAPI**, a high-performance Python web framework for building APIs.
- **Database:** **PostgreSQL** (or any other SQLAlchemy-compatible relational database).
- **ORM:** **SQLAlchemy** is used as the Object-Relational Mapper to interact with the database using Python models.
- **Data Validation:** **Pydantic** is used for data validation, serialization, and settings management, ensuring that all data flowing into and out of the API is well-formed.
- **Authentication:** **JWT (JSON Web Tokens)** are used for securing endpoints. Password hashing is handled by **Passlib** with the `bcrypt` algorithm.
- **Asynchronous Operations:** Built on top of **Uvicorn** and **Starlette**, the API is fully capable of asynchronous request handling for high concurrency.

## Project Layout

The codebase is organized into the following directories:

```
/farlab-inventory-backend
|-- .env                # Environment variables (database URL, secret keys)
|-- main.py             # Main FastAPI application file, middleware, and startup events
|-- database.py         # Database engine, session management, and table creation
|-- requirements.txt    # Python package dependencies
|
|-- /models/            # SQLAlchemy ORM models (defines database table structures)
|   |-- user.py
|   |-- instrument.py
|   |-- part.py
|   `-- ...
|
|-- /schemas/           # Pydantic models (defines API request/response shapes)
|   |-- user.py
|   |-- instrument.py
|   |-- part.py
|   `-- ...
|
|-- /routers/           # API endpoint logic, grouped by resource
|   |-- auth.py
|   |-- users.py
|   |-- instruments.py
|   `-- parts.py
|
`-- /utils/             # Reusable utility functions and dependencies
    |-- security.py       # Password hashing, JWT creation/decoding
    `-- dependencies.py   # FastAPI dependencies (e.g., get_current_user)
```

## Database Schema

The following tables are defined in the database. Relationships are managed by SQLAlchemy.

- **`users`**: Stores user information, credentials, and roles.
  - `id`, `username`, `email`, `hashed_password`, `is_admin`, `is_active`, etc.

- **`instruments`**: Stores information about laboratory instruments.
  - `id`, `name`, `model`, `manufacturer`, `serial_number`, etc.

- **`parts`**: Stores information about all inventory parts.
  - `id`, `part_number`, `name`, `quantity_in_stock`, `minimum_stock_level`, etc.

- **`instrument_parts`**: An association table linking instruments to the parts they use (many-to-many relationship).
  - `instrument_id` (FK to `instruments.id`)
  - `part_id` (FK to `parts.id`)

- **`alerts`**: Stores records of low-stock alerts.
  - `id`, `part_id`, `message`, `is_resolved`, etc.

## API Endpoints

For a full, interactive list of all API endpoints, their parameters, and response models, please run the server and visit the auto-generated documentation at **`http://localhost:8000/docs`**.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd farlab-inventory-backend
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    - Create a file named `.env` in the project root.
    - Add the following required variables. Generate a strong `SECRET_KEY` and use your actual database connection string.

    ```env
    # Example for a local PostgreSQL database
    DATABASE_URL=postgresql://user:password@localhost/farlab_inventory

    # Generate with `openssl rand -hex 32`
    SECRET_KEY=your_super_secret_random_string

    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

## Running the Server

Once the setup is complete, you can run the development server using Uvicorn.

```bash
uvicorn main:app --reload
```

- The server will be available at `http://localhost:8000`.
- The `--reload` flag enables hot-reloading, so the server will automatically restart when you make changes to the code.
