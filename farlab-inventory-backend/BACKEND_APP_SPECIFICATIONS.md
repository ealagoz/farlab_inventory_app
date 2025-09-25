# FarLab Inventory Backend Specifications

This document outlines the core features and functionality of the FarLab Inventory Backend application.

## Core Features

*   **User Management**: Create, retrieve, update, and delete users.
*   **Authentication**: Secure user login and registration with JWT-based authentication.
*   **Instrument Management**: Manage laboratory instruments, including their parts and specifications.
*   **Part Management**: Track individual parts, their stock levels, and associations with instruments.
*   **Alerting System**: A system for creating and managing alerts, likely related to inventory levels or instrument status.
*   **Scheduled Tasks**: The `scheduler.py` service suggests the ability to run background tasks at specified intervals.

## API Endpoints

The API is organized into the following routers:

*   `/auth`: Handles user authentication, including login and token generation.
*   `/users`: Provides CRUD operations for user management.
*   `/instruments`: Provides CRUD operations for managing instruments.
*   `/parts`: Provides CRUD operations for managing parts.
*   `/alerts`: Provides CRUD operations for the alerting system.

## Database Schema

The database schema is defined using SQLAlchemy models in the `models/` directory. The key models are:

*   **`User`**: Stores user information, including credentials.
*   **`Instrument`**: Represents a laboratory instrument.
*   **`Part`**: Represents a part that can be used in an instrument.
*   **`InstrumentPart`**: A many-to-many relationship table between instruments and parts.
*   **`Alert`**: Stores information about alerts.

## Authentication

Authentication is handled using JSON Web Tokens (JWT). The process is as follows:

1.  A user submits their credentials to the `/auth/token` endpoint.
2.  The `auth_service` verifies the credentials.
3.  If the credentials are valid, a JWT is generated and returned to the user.
4.  The user must include this JWT in the `Authorization` header of subsequent requests to protected endpoints.
5.  A FastAPI dependency (`get_current_user`) verifies the JWT and retrieves the current user for each request.
