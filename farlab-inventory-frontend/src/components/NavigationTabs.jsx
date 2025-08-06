// NavigationTabs: Instrument Tabs
import React from "react";
import { useState, useEffect } from "react";
import { NavLink } from "react-router-dom";
import { useAppContext } from "../context/AppContext";
import apiFetch, { getAlertSummary } from "../utils/api";
import logger from "../utils/logger";
import "./NavigationTabs.css";
export function NavigationTabs() {
  const {
    instruments,
    isSearchActive,
    setInstruments,
    setInstrumentsLoading,
    alertSummary,
  } = useAppContext();
  const [error, setError] = useState(null);

  logger.log("--- NavigationTabs Component Rendered ---");

  useEffect(() => {
    logger.log("==> NavigationTabs useEffect triggered.");

    // Fetch instrumentData and alery summary data when the components mounts
    const fetchInstruments = async () => {
      // Set a global loading state True before fetching
      setInstrumentsLoading(true);
      try {
        logger.log("Setting global instrumentsLoading to TRUE.");
        const instrumentsData = await apiFetch("/instruments/");

        logger.log("Successfully fetched instruments:", instrumentsData);
        setInstruments(instrumentsData || []); // Ensure data is an array
        setError(null);
      } catch (err) {
        setError(err.message);
        logger.error("Failed to fetch instruments: ", err);
      } finally {
        logger.log(
          "Setting global instrumentsLoading to FALSE in finally block."
        );
        setInstrumentsLoading(false);
      }
    };
    fetchInstruments();
  }, [setInstruments, setInstrumentsLoading]); // Empty dependency array means this effect runs only once

  // Derive count directly from the context's summary object
  const activeAlertsCount = alertSummary?.active_alerts || 0;

  if (error) {
    logger.log("NavigationTabs decision: Rendering ERROR message.");
    return <nav className="navigation-tabs">Error: {error}</nav>;
  }

  logger.log(
    `NavigationTabs decision: Rendering ${instruments.length} nav links.`
  );
  logger.log("-----------------------------------------");

  return (
    <nav className={`navigation-tabs ${isSearchActive ? "search-active" : ""}`}>
      {instruments.map((instrument) => (
        <NavLink
          key={instrument.id}
          to={`/instruments/${instrument.name.toLowerCase()}`}
          className={({ isActive }) => `nav-tab ${isActive ? "active" : ""}`}
        >
          {instrument.name}
          {/* Add part counts here*/}
        </NavLink>
      ))}
      <NavLink
        to="/alerts"
        className={({ isActive }) =>
          `nav-tab alert-tab ${isActive ? "active" : ""}`
        }
      >
        Alerts
        {activeAlertsCount > 0 && (
          <span className="alert-badge">{activeAlertsCount}</span>
        )}
      </NavLink>
    </nav>
  );
}

export default NavigationTabs;
