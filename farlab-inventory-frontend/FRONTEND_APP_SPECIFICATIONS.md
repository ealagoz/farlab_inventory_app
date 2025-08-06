# FarLab Inventory Frontend Specifications

## 1. Introduction

This document provides a comprehensive overview of the FarLab Inventory Frontend application. This application is a single-page application (SPA) built with React, designed to interact with the FarLab Inventory Backend API. It provides a user-friendly interface for managing laboratory inventory, including instruments and parts.

## 2. Technology Stack

The application is built using the following technologies:

*   **Frontend Library**: [React](https://reactjs.org/)
*   **Routing**: [React Router](https://reactrouter.com/)
*   **Build Tool**: [Vite](https://vitejs.dev/)
*   **Linting**: [ESLint](https://eslint.org/)
*   **Package Manager**: [npm](https://www.npmjs.com/)

## 3. Project Structure

The project is organized into the following directories and files:
/
├── .env.local
├── .gitignore
├── CODEBASE_OVERVIEW.md
├── eslint.config.js
├── FRONTEND_APP_SPECIFICATIONS.md
├── index.html
├── Layout.css
├── Layout.jsx
├── package-lock.json
├── package.json
├── README.md
├── vite.config.js
├── node_modules/
├── public/
│   └── vite.svg
└── src/
    ├── App.css
    ├── App.jsx
    ├── index.css
    ├── main.jsx
    ├── assets/
    │   ├── farlab_logo.png
    │   └── react.svg
    ├── components/
    │   ├── ErrorBoundary.jsx
    │   ├── Header.jsx
    │   ├── LoadingSpinner.jsx
    │   ├── NavigationTabs.jsx
    │   ├── PartForm.jsx
    │   ├── PartItem.jsx
    │   ├── PartsTable.jsx
    │   ├── ProtectedRoute.jsx
    │   ├── SearchBox.jsx
    │   └── SearchResults.jsx
    ├── context/
    │   └── AppContext.jsx
    ├── hooks/
    │   ├── useAuth.js
    │   ├── useDebounce.js
    │   └── useSearch.js
    ├── pages/
    │   ├── AlertsPage.jsx
    │   ├── InstrumentPage.jsx
    │   └── LoginPage.jsx
    └── utils/
        ├── api.js
        ├── logger.js
        └── styleUtils.js

## 4. Core Features

The application provides the following core features:

*   **User Authentication**: Secure login page for users to access the application.
*   **Instrument Management**: View and manage laboratory instruments and their associated parts.
*   **Part Management**: Search for parts and view their details.
*   **Alerts**: A dedicated page to display alerts, likely related to inventory levels.
*   **Protected Routes**: Ensures that only authenticated users can access the main application.
*   **Robust Error Handling**: The application is wrapped in an Error Boundary to prevent crashes from UI rendering errors and to display a user-friendly fallback screen.

## 5. Component-Based Architecture

The frontend is built using a component-based architecture, with reusable components for different UI elements. Key components include:

*   **`ErrorBoundary`**: A component that catches JavaScript errors anywhere in the app, preventing a full crash and displaying a fallback UI.
*   **`Header`**: The main header of the application, including the logo and navigation.
*   **`NavigationTabs`**: Tabs for navigating between different sections of the application.
*   **`PartsTable`**: A table for displaying a list of parts.
*   **`SearchBox`**: A search input for finding parts.
*   **`LoginPage`**: A dedicated page for user login.
*   **`InstrumentPage`**: A page for displaying instrument details and associated parts.
*   **`AlertsPage`**: A page for displaying alerts.

## 6. State Management

Global application state is managed using React's Context API, specifically in `src/context/AppContext.jsx`. This includes user authentication status, alert data, and other shared data, along with centralized error handling for API calls.

## 7. Authentication Flow

Authentication is handled as follows:

1.  The user navigates to the `/login` page and enters their credentials.
2.  The `useAuth` hook handles the API call to the backend's `/auth/token` endpoint.
3.  Upon successful authentication, a JWT is received and stored in local storage.
4.  The `ProtectedRoute` component checks for the presence of a valid token before rendering protected pages.
5.  The `api.js` utility attaches the JWT to the `Authorization` header of all subsequent API requests.

## 8. Running the Application

To run the application locally, follow these steps:

1.  **Install Dependencies**:
    ```bash
    npm install
    ```

2.  **Set up Environment Variables**:
    Create a `.env.local` file in the root directory and add the necessary configuration variables, such as the backend API URL.

3.  **Run the Development Server**:
    ```bash
    npm run dev
    ```

The application will be available at `http://localhost:5173` by default.

## 9. Future Improvements

*   **Add End-to-End Testing**: Implement a testing suite with a framework like Cypress or Playwright.
*   **Component Storybook**: Create a Storybook to document and test UI components in isolation.
*   **Add More Pages**: Create pages for user management and other features as the backend API expands.
