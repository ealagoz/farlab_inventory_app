// src/components/SearchResults.jsx
import React from "react";
import { useAppContext } from "../context/AppContext";
import LoadingSpinner from "./LoadingSpinner";
import PartItem from "./PartItem";
import "./SearchResults.css";
import { getStatusClass } from "../utils/styleUtils";

export function SearchResults() {
  const { searchResults, searchLoading, searchError } = useAppContext();

  if (searchLoading) {
    return <LoadingSpinner />;
  }

  if (searchError) {
    return <div className="search-error">Error: {searchError}</div>;
  }

  if (!searchResults) {
    return null;
  }

  if (searchResults.length === 0) {
    return <div className="no-results">No parts found.</div>;
  }

  return (
    <div className="search-results-container">
      <h2 className="results-header">Search Results</h2>
      <div className="table-container">
        <table className="parts-table">
          <thead>
            <tr>
              <th>Part Number</th>
              <th>Name</th>
              <th>In Stock</th>
              <th>Status</th>
              <th>Instrument</th>
            </tr>
          </thead>
          <tbody>
            {searchResults.map((part) => (
              <tr key={part.id} className="part-item">
                <td>{part.part_number || "N/A"}</td>
                <td>{part.name}</td>
                <td>{part.quantity_in_stock}</td>
                <td>
                  <span
                    className={`status-badge ${getStatusClass(
                      part.stock_status
                    )}`}
                  >
                    {part.stock_status}
                  </span>
                </td>
                {/* <td>{part.manufacturer || "N/A"}</td> */}
                <td>
                  <div className="instrument-tags-container">
                    {
                      part.instruments && part.instruments.length > 0
                        ? part.instruments.map((inst) => (
                            <span key={inst.id} className="instrument-tag">
                              {inst.name}
                            </span>
                          ))
                        : "N/A" // Show N/A if no instruments are linked
                    }
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default SearchResults;
