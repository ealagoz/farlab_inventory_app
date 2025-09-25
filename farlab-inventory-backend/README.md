# FARLAB Inventory Management System - Backend

This repository contains the backend server for the FARLAB Inventory Management System. It is a robust, secure, and efficient API built with FastAPI that provides all the necessary endpoints to manage laboratory instruments, parts, users, and stock alerts.

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

    Create a file named `.env` in the project root.

    ```env
    DATABASE_URL=postgresql://user:password@localhost/farlab_inventory
    SECRET_KEY=your_super_secret_random_string
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

## Running the Server

```bash
uvicorn main:app --reload
```

- The server will be available at `http://localhost:8000`.
- The `--reload` flag enables hot-reloading, so the server will automatically restart when you make changes to the code.

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
