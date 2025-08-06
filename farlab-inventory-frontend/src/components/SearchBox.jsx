// src/components/SearchBox.jsx
import React from "react";
import { useAppContext } from "../context/AppContext";
import "./SearchBox.css";

export function SearchBox() {
  const { searchQuery, setSearchQuery } = useAppContext();

  const handleClear = () => {
    setSearchQuery("");
  };

  return (
    <div className="search-box-container">
      <input
        type="text"
        className="search-input"
        placeholder="Search for parts across all instruments..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />
      {searchQuery && (
        <button onClick={handleClear} className="clear-button">
          &times;
        </button>
      )}
    </div>
  );
}

export default SearchBox;
