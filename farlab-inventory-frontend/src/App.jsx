// App: Main Router + Global State
import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import AppProvider from "./context/AppContext";
import Layout from "../Layout";
import InstrumentPage from "./pages/InstrumentPage";
import LoginPage from "./pages/LoginPage";
import AlertsPage from "./pages/AlertsPage";
import ProtectedRoute from "./components/ProtectedRoute";
import "./App.css";

export function App() {
  return (
    // Wrap the entire application with AppProvider
    <AppProvider>
      <BrowserRouter>
        <Routes>
          {/* Publicly accessible login route */}
          <Route path="/login" element={<LoginPage />} />
          {/* Protected routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route
              index
              element={<Navigate to="/instruments/mat253" replace />}
            />
            {/* Add future protected routes here, e.g. for editing */}
            <Route path="alerts" element={<AlertsPage />} />
            <Route
              path="instruments/:instrumentType"
              element={<InstrumentPage />}
            />
          </Route>
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}

export default App;
