// src/utils/api.js

import logger from "./logger";

// Determine the correct API URL based on environment
const getApiBaseUrl = () => {
  logger.log("Initializing API base URL...");

  // The browser always needs to use localhost, not Docker service names
  // Docker service names (like 'backend') only work inside the Docker network

  if (import.meta.env.VITE_API_URL) {
    console.log("Using VITE_API_URL:", import.meta.env.VITE_API_URL);
    // If VITE_API_URL contains 'backend:', replace with localhost for browser
    if (import.meta.env.VITE_API_URL.includes("backend:")) {
      const browserUrl = import.meta.env.VITE_API_URL.replace(
        "backend:",
        "localhost:"
      );
      logger.log("Using configured VITE_API_URL");
      return browserUrl;
    }
    return import.meta.env.VITE_API_URL;
  }

  // Default for browser access
  const defaultUrl = "http://localhost:8000";
  logger.log("Using default API URL");
  return defaultUrl;
};

const API_BASE_URL = getApiBaseUrl();
logger.log("Using final API_BASE_URL");

// A utility for fetching data from the backend API
async function apiFetch(endpoint, options = {}) {
  // Ensure endpoint starts with /
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;

  // Add /api prefix if not already present
  const apiEndpoint = cleanEndpoint.startsWith("/api")
    ? cleanEndpoint
    : `/api${cleanEndpoint}`;
  // const apiEndpoint = cleanEndpoint; // Changed 03/09/2025 EA

  const url = `${API_BASE_URL}${apiEndpoint}`;

  logger.log("Making API request to:", url);

  // Default headers
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  // Check for and add auth token if it exists
  const token = localStorage.getItem("authToken");
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const detail =
        errorData.detail || `HTTP error! status: ${response.status}`;
      const errorMessage =
        typeof detail === "object" ? JSON.stringify(detail, null, 2) : detail;
      throw new Error(errorMessage);
    }

    if (response.status === 204) {
      return null;
    }

    return await response.json();
  } catch (error) {
    logger.error("API fetch error:", error.message);
    logger.error("Failed URL:", url);
    throw error;
  }
}

export default apiFetch;

// Rest of your existing functions...
export const setAuthToken = (token) => {
  localStorage.setItem("authToken", token);
};

export const removeAuthToken = () => {
  localStorage.removeItem("authToken");
};

export const getAuthToken = () => {
  return localStorage.getItem("authToken");
};

export const getAlerts = () => {
  return apiFetch("/api/alerts/?active_only=true");
};

export const getAlertSummary = () => {
  return apiFetch("/api/alerts/summary");
};
