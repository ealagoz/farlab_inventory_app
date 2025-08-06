// Layout: Header + Navigation + Main Content
import React from "react";
import { Outlet } from "react-router-dom";
import Header from "./src/components/Header";
import logger from "./src/utils/logger";
import NavigationTabs from "./src/components/NavigationTabs";
import SearchResults from "./src/components/SearchResults";
import { useAppContext } from "./src/context/AppContext";
import "./Layout.css";

const Layout = () => {
  const { isSearchActive } = useAppContext();

  logger.log("--- Layout Component Re-rendering ---");
  logger.log(`isSearchActive state is: ${isSearchActive}`);
  if (isSearchActive) {
    logger.log("Render decision: SHOWING SEARCH RESULTS");
  } else {
    logger.log("Render decision: SHOWING OUTLET (for InstrumentPage)");
  }
  logger.log("------------------------------------");

  return (
    <div className="app-layout">
      <Header />
      <NavigationTabs />
      <main className="app-content">
        {/* Conditionally render search results of the page content */}
        {isSearchActive ? <SearchResults /> : <Outlet />}
      </main>
      <footer className="app-footer">
        <p>Copyright © 2025 FARLAB</p>
      </footer>
    </div>
  );
};

export default Layout;
