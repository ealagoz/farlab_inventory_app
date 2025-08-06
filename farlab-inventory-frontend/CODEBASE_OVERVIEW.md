# FARLAB Inventory Frontend: Codebase Overview

## 1. Project Overview

This document provides a technical overview of the FARLAB Inventory frontend application. The application is a web-based client designed to manage and track inventory for various instruments. It features user authentication, a searchable parts database, and the ability to perform CRUD (Create, Read, Update, Delete) operations on inventory items.

## 2. Core Technologies

*   **Framework:** [React](https://reactjs.org/) (v18+) is the core library for building the user interface. The codebase uses functional components with Hooks extensively.
*   **Build Tool:** [Vite](https://vitejs.dev/) serves as the build tool and development server, providing a fast and modern development experience with features like Hot Module Replacement (HMR).
*   **Routing:** [React Router DOM](https://reactrouter.com/) is used for client-side routing, enabling navigation between different pages (e.g., `/login`, `/instrument/:instrumentType`) without full page reloads.
*   **Language:** JavaScript (ES6+) with JSX syntax.

## 3. Project Structure & Architecture

The project follows a standard, feature-oriented structure that separates concerns into distinct directories within the `src/` folder.

```
/src
├── assets/         # Static assets like images (e.g., SVGs)
├── components/     # Reusable UI components (e.g., PartsTable, Header, PartForm)
├── context/        # React Context for global state management (AppContext)
├── hooks/          # Custom React Hooks for reusable logic (e.g., useAuth, useSearch)
├── pages/          # Top-level components representing application pages (e.g., LoginPage, InstrumentPage)
└── utils/          # Utility functions (e.g., api.js for API calls, logger.js)
```

*   **Component-Based Architecture:** The UI is broken down into a hierarchy of reusable components. `App.jsx` serves as the entry point, setting up the main `Layout.jsx` which contains the header, navigation, and the main content area where pages are rendered.
*   **Separation of Concerns:**
    *   **Pages** are responsible for fetching data and composing layouts from smaller **Components**.
    *   **Components** are designed to be reusable and are responsible for rendering specific pieces of the UI.
    *   **Hooks** encapsulate business logic and stateful operations, making them reusable across different components.
    *   **Context** provides a centralized store for global application state.

## 4. State Management

Global state management is handled by **React's Context API**, implemented in `src/context/AppContext.jsx`. This context provider centralizes critical application-wide state, such as:

*   Authenticated user information (`currentUser`).
*   The main list of instruments.
*   Search state (`isSearchActive`, `searchResults`, etc.).

This approach avoids "prop drilling" and provides a clean way for any component in the tree to access or modify global state.

## 5. API Communication

The frontend communicates with a backend server via a **RESTful API**.

*   **API Abstraction:** All API calls are handled through a centralized utility function in `src/utils/api.js`. This `apiFetch` function wraps the native `fetch` API, providing a consistent way to handle requests, set headers (e.g., for authentication), and process responses.
*   **Data Fetching:** Data is fetched within page components (e.g., `InstrumentPage.jsx`) using the `useEffect` and `useCallback` hooks to manage the lifecycle of API requests, handle loading states, and catch errors.

## 6. Styling

Styling is handled with **plain CSS**. Each component or page has its own corresponding `.css` file (e.g., `Header.css`, `InstrumentPage.css`). This approach keeps styles scoped to their respective components. Global styles and CSS variable definitions are located in `src/App.css` and `src/index.css`.
