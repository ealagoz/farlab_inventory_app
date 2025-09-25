# FarLab Inventory Frontend Specifications

This document outlines the core features and functionality of the FarLab Inventory Frontend application.

## Core Features

*   **User Authentication**: A secure login page allows users to access the application.
*   **Instrument Management**: Users can view and manage laboratory instruments and their associated parts.
*   **Part Management**: Users can search for parts and view their details.
*   **Alerts**: A dedicated page displays alerts related to inventory levels.
*   **Protected Routes**: The application uses protected routes to ensure that only authenticated users can access sensitive data.
*   **Error Handling**: A robust Error Boundary prevents the UI from crashing and provides a better user experience.

## Authentication Flow

1.  The user enters their credentials on the `/login` page.
2.  The `useAuth` hook sends an API request to the backend to authenticate the user.
3.  Upon successful authentication, a JWT is stored in local storage.
4.  The `ProtectedRoute` component verifies the token before rendering protected pages.
5.  The `api.js` utility includes the JWT in the `Authorization` header for all subsequent API requests.
