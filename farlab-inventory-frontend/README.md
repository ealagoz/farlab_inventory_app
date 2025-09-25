## FarLab Inventory Management System

This repository contains the frontend for the FarLab Inventory Management System, a single-page application (SPA) built with React. It provides a user-friendly interface for managing laboratory equipment and parts.

### Project Structure

- **`src/`**: Contains all the source code for the application.
- **`src/components/`**: Reusable UI components.
- **`src/pages/`**: Top-level components that represent the different pages of the application.
- **`src/hooks/`**: Custom React hooks for reusable logic.
- **`src/context/`**: React context for global state management.
- **`src/utils/`**: Utility functions for API calls, logging, etc.

### Getting Started

1.  **Clone the repository:**

    ```bash
    git clone <your-repository-url>
    cd <your-repository-name>/farlab-inventory-frontend
    ```

2.  **Install dependencies:**

    ```bash
    npm install
    ```

3.  **Set up environment variables:**

    Create a `.env.local` file and add the following:

    ```
    VITE_API_BASE_URL="http://127.0.0.1:8000/api"
    ```

4.  **Run the development server:**

    ```bash
    npm run dev
    ```
