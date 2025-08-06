// src/hooks/useAuth.js
import { useState, useEffect, useCallback } from "react";
import apiFetch, {
  setAuthToken,
  removeAuthToken,
  getAuthToken,
} from "../utils/api";
import logger from "../utils/logger";

// A helper function to decode the JWT token
const decodeToken = (token) => {
  try {
    // Decode the payload part of the token
    const payload = JSON.parse(atob(token.split(".")[1]));
    return {
      userId: payload.user_id,
      username: payload.username,
      exp: payload.exp,
    };
  } catch (error) {
    logger.error("Failed to decode token:", error);
    return null;
  }
};

export function useAuth() {
  const [currentUser, setCurrentUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true); // To check initial auth status

  // Check for an existing token on initial component auth
  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      const decoded = decodeToken(token);
      // Check if the token is expired
      if (decoded && decoded.exp * 1000 > Date.now()) {
        setCurrentUser(decoded);
        // Ensure the token is et for API calls on refresh
        setAuthToken(token);
      } else {
        // Clear expired token
        removeAuthToken();
      }
    }
    setAuthLoading(false);
  }, []);

  const login = useCallback(async (username, password) => {
    try {
      // The backend expects form data for the token endpoint
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const data = await apiFetch("/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData.toString(),
      });
      if (data.access_token) {
        setAuthToken(data.access_token);
        const decoded = decodeToken(data.access_token);
        setCurrentUser(decoded);
      } else {
        throw new Error("Login failed: No access token received.");
      }
    } catch (error) {
      logger.error("Login error:", error);
      // Re-throw to be caught by the component
      throw error;
    }
  }, []);

  const logout = useCallback(() => {
    removeAuthToken();
    setCurrentUser(null);
  }, []);

  return { currentUser, login, logout, authLoading };
}
