// src/utils/api.js

import logger from "./logger";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

// A utility for fetching data from the backend API
async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

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
      // Parse the JSON error body from the backend
      const errorData = await response.json().catch(() => ({}));
      // Create a more informative message.
      const detail =
        errorData.detail || `HTTP error! status: ${response.status}`;
      // If the detail is an object (like FASTAPI validation errors), stringify it.
      const errorMessage =
        typeof detail === "object" ? JSON.stringify(detail, null, 2) : detail;
      throw new Error(errorMessage);
    }

    // If the response is successful but has no content
    if (response.status === 204) {
      return null;
    }

    return await response.json();
  } catch (error) {
    logger.error("API fetch error:", error.message);
    // Re-throw the error so that calling components can handle it
    throw error;
  }
}

export default apiFetch;

// Utility functions for auth tokens
export const setAuthToken = (token) => {
  localStorage.setItem("authToken", token);
};

export const removeAuthToken = () => {
  localStorage.removeItem("authToken");
};

export const getAuthToken = () => {
  return localStorage.getItem("authToken");
};

// --- Alert Endpoints ---
/**
 * Fetches alerts from the backend.
 * By default, the backend will return only active alerts.
 * @returns {Promise<Array>} A promise that resolves to an array of alert.
 */
export const getAlerts = () => {
  return apiFetch("/alerts/?active_only=true");
};

/**
 * Fetches alert summary statistics.
 * @returns (Promise<Object>) A promise that resolves to the alert summary object.
 */
export const getAlertSummary = () => {
  return apiFetch("/alerts/summary");
};

// /**
//  * Triggers a check for low stock parts and creates alerts.
//  * @returns {Promise<Object>} A promise that resolves to the result of the check.
//  */
// export const checkLowStockAlerts = () => {
//   return apiFetch("/alerts/check", { method: "POST" });
// };
