# FarLab Inventory Management System

This is the main repository for the FarLab Inventory Management System, a comprehensive full-stack application designed for tracking and managing laboratory equipment and parts.

## Overview

The system is composed of two main parts:

*   **A React Frontend**: A modern, responsive single-page application (SPA) that provides a user-friendly interface for interacting with the inventory data.
*   **A Python Backend**: A robust RESTful API built with FastAPI that handles all business logic, data storage, and user authentication.

## Core Features

*   **User Authentication**: Secure user login with JWT-based authentication.
*   **Instrument & Part Management**: Full CRUD (Create, Read, Update, Delete) operations for instruments and their associated parts.
*   **Global Search**: A fast, debounced search feature to find parts across all instruments.
*   **Alerting System**: A dedicated page to view low-stock alerts and other important notifications.
*   **Protected Routes**: Frontend routes are protected to ensure only authenticated users can access sensitive data.
*   **Error Handling**: A robust Error Boundary in the frontend prevents UI crashes and provides a better user experience.

## Technology Stack

### Frontend

*   **Library/Framework**: [React](https://reactjs.org/) (v19+)
*   **Build Tool**: [Vite](https://vitejs.dev/)
*   **Routing**: [React Router](https://reactrouter.com/)
*   **Styling**: Plain CSS with a modular, component-based approach.
*   **Linting**: [ESLint](https://eslint.org/)

### Backend

*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
*   **Web Server**: [Uvicorn](https://www.uvicorn.org/)
*   **Database**: [PostgreSQL](https://www.postgresql.org/)
*   **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
*   **Authentication**: JWT with `python-jose` and `passlib`
*   **Environment Management**: `pyenv` and `pip` with `requirements.txt`

## Getting Started

To run this project locally, you will need to set up both the backend and the frontend. It is recommended to open two separate terminal windows for this process.

### 1. Backend Setup

First, set up and run the backend server.

**Clone the repository:**

```bash
git clone <your-repository-url>
cd <your-repository-name>/farlab-inventory-backend
```

**Set up the Python environment (using `pyenv`):**

```bash
# Install the correct Python version
pyenv install

# Create and activate a virtual environment
pyenv virtualenv <python-version> farlab-inventory-backend
pyenv local farlab-inventory-backend
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Set up environment variables:**

Create a file named `.env` in the `farlab-inventory-backend` directory and add the necessary variables, such as your `DATABASE_URL` and `SECRET_KEY`.

```
DATABASE_URL="postgresql://user:password@host:port/database"
SECRET_KEY="your_super_secret_key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Run the backend server:**

```bash
uvicorn main:app --reload
```

The backend API should now be running at `http://127.0.0.1:8000`.

### 2. Frontend Setup

In a new terminal window, navigate to the frontend directory.

```bash
cd ../farlab-inventory-frontend
```

**Install dependencies:**

```bash
npm install
```

**Set up environment variables:**

Create a file named `.env.local` in the `farlab-inventory-frontend` directory. This file will tell your frontend where to find the backend API.

```
VITE_API_BASE_URL="http://127.0.0.1:8000/api"
VITE_LOGGING_ENABLED=true
```

## Running the Application

Once both the backend and frontend setup steps are complete, you can run the frontend development server.

```bash
npm run dev
```

The frontend application will be available at `http://localhost:5173` (or another port if 5173 is in use).

## API Documentation

The backend provides auto-generated API documentation. Once the backend server is running, you can access it at:

*   **Swagger UI**: `http://127.0.0.1:8000/docs`
*   **ReDoc**: `http://127.0.0.1:8000/redoc`