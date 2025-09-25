# Codebase Overview

This document provides a technical overview of the FARLAB Inventory frontend application, focusing on its architecture and the roles of its key directories.

## Project Structure

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

## Component-Based Architecture

The UI is broken down into a hierarchy of reusable components. `App.jsx` serves as the entry point, setting up the main `Layout.jsx` which contains the header, navigation, and the main content area where pages are rendered.

-   **Pages**: Responsible for fetching data and composing layouts from smaller **Components**.
-   **Components**: Designed to be reusable and are responsible for rendering specific pieces of the UI.
-   **Hooks**: Encapsulate business logic and stateful operations, making them reusable across different components.
-   **Context**: Provides a centralized store for global application state.

## State Management

Global state management is handled by **React's Context API**, implemented in `src/context/AppContext.jsx`. This context provider centralizes critical application-wide state, such as:

-   Authenticated user information (`currentUser`).
-   The main list of instruments.
-   Search state (`isSearchActive`, `searchResults`, etc.).

## API Communication

All API calls are handled through a centralized utility function in `src/utils/api.js`. This `apiFetch` function wraps the native `fetch` API, providing a consistent way to handle requests, set headers (e.g., for authentication), and process responses.
