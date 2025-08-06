import React, {
  createContext,
  useState,
  useMemo,
  useContext,
  useCallback,
  useEffect,
} from "react";
import { useSearch } from "../hooks/useSearch";
import { useAuth } from "../hooks/useAuth";
import { getAlerts, getAlertSummary } from "../utils/api";
import logger from "../utils/logger";

// 1. Create the context
const AppContext = createContext(null);

// 2. Create the Provider component
export default function AppProvider({ children }) {
  // State for authentication from custom hooks
  const { currentUser, login, logout, authLoading } = useAuth(); // useAuth hook
  // State for search functionality
  const [searchQuery, setSearchQuery] = useState("");
  const { searchResults, searchLoading, searchError } = useSearch(searchQuery);

  // State for navigation badges
  const [instrumentPartCounts, setInstrumentPartCounts] = useState({});
  // State for instruments
  const [instruments, setInstruments] = useState([]);
  // State for tracking if the initial instrument list is loading
  const [instrumentsLoading, setInstrumentsLoading] = useState(true);

  // Centralized state for alerts
  const [alertSummary, setAlertSummary] = useState({});
  const [activeAlerts, setActiveAlerts] = useState([]);
  const [alertsLoading, setAlertsLoading] = useState(true);
  const [alertsError, setAlertsError] = useState(null);

  // Function to refresh alert data from the server
  const refreshAlertData = useCallback(async () => {
    logger.log("Context: Refreshing alert data...");
    setAlertsLoading(true);
    setAlertsError(null);
    try {
      const [summaryData, alertsData] = await Promise.all([
        getAlertSummary(),
        getAlerts(),
      ]);
      setAlertSummary(summaryData);
      setActiveAlerts(alertsData);
    } catch (error) {
      logger.error("Context: Failed to refresh alert data:", error);
      setAlertsError(error.message); // Set the error state
    } finally {
      setAlertsLoading(false);
    }
  }, []);

  // Fetch initial alert data when the app first loads
  useEffect(() => {
    if (currentUser) {
      // Only fetch if user is logged in
      refreshAlertData();
    }
  }, [currentUser, refreshAlertData]);

  // Derived state: Search is active if the query not empty
  // This doesnot need to be a separate state variable
  const isSearchActive = searchQuery.trim() !== "";

  // 3. Memoize the context value to prevent unnecessary re-renders
  const contextValue = useMemo(
    () => ({
      // Auth values
      currentUser,
      login,
      logout,
      authLoading,
      // Search values
      searchQuery,
      setSearchQuery,
      searchResults,
      searchLoading,
      searchError,
      isSearchActive,
      // Instrument values
      instruments,
      setInstruments,
      instrumentsLoading,
      setInstrumentsLoading,
      instrumentPartCounts,
      setInstrumentPartCounts,
      // Alert values
      alertSummary,
      activeAlerts,
      alertsLoading,
      alertsError,
      refreshAlertData,
    }),
    [
      currentUser,
      authLoading,
      login,
      logout,
      searchQuery,
      searchResults,
      searchLoading,
      searchError,
      isSearchActive,
      instruments,
      instrumentsLoading,
      instrumentPartCounts,
      alertSummary,
      activeAlerts,
      alertsLoading,
      alertsError,
      refreshAlertData,
    ]
  );

  return (
    <AppContext.Provider value={contextValue}>{children}</AppContext.Provider>
  );
}

// 4. Create a custom hook for easy access to the context
export const useAppContext = () => {
  const context = useContext(AppContext);
  if (context === null) {
    throw new Error("useAppContext must be used within an AppProvider");
  }
  return context;
};
