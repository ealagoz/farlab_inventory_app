// src/hooks/useAuth.js
import { useState, useEffect, useCallback } from "react";
import apiFetch, {
  setAuthToken,
  removeAuthToken,
  getAuthToken,
} from "../utils/api";
import logger from "../utils/logger";

export function useAuth() {
  const [currentUser, setCurrentUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true); // To check initial auth status

  // Check for an existing token on initial component auth
  useEffect(() => {
    const validateExistingToken = async () => {
      const token = getAuthToken();
      if (token) {
        try {
          setAuthToken(token); // Set token for API calls
          const userData = await apiFetch("/api/users/me");
          setCurrentUser({
            userId: userData.id,
            username: userData.username,
            email: userData.email,
          });
          logger.log("Token validated successfully");
        } catch (error) {
          logger.error("Token validation failed:", error);
          removeAuthToken();
        }
      }
      setAuthLoading(false);
    };
    validateExistingToken();
  }, []);

  const login = useCallback(async (username, password) => {
    try {
      // The backend expects form data for the token endpoint
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const data = await apiFetch("/api/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData.toString(),
      });
      if (data.access_token) {
        setAuthToken(data.access_token);

        // Validate token with server instead of decoding
        const userData = await apiFetch("/api/users/me");
        setCurrentUser({
          userId: userData.id,
          username: userData.username,
          email: userData.email,
        });
        logger.log("Login successful");
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
