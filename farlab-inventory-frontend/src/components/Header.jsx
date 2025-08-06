// src/components/Header.jsx
import React from "react";
import { useNavigate } from "react-router-dom";
import { useAppContext } from "../context/AppContext";
import farlabLogo from "../assets/farlab_logo.png";
import SearchBox from "./SearchBox";
import "./Header.css";

export function Header() {
  const { currentUser, logout } = useAppContext();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login"); // Redirect to login page after logout
  };

  return (
    <header className="app-header">
      <div className="logo">
        <a
          href="https://www.uib.no/en/FARLAB"
          target="_blank" // <-- Open the link in a new tab
          rel="noopener noreferrer" // <-- for security
        >
          <img src={farlabLogo} alt="FARLAB Logo" className="logo-img" />
        </a>
        <a href="/">FARLAB Inventory</a>
      </div>
      <div className="search-container">
        <SearchBox />
      </div>
      <div className="user-menu">
        {/* UserMenu will go here */}
        {currentUser ? (
          <>
            <span className="user-greeting">
              Welcome, {currentUser.username}
            </span>
            <button onClick={handleLogout} className="logout-button">
              Logout
            </button>
          </>
        ) : (
          // Either leave this empty or add a login
          <span></span>
        )}
      </div>
    </header>
  );
}

export default Header;
