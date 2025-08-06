// src/hooks/useSearch.js
import { useState, useEffect } from "react";
import { useDebounce } from "./useDebounce";
import apiFetch from "../utils/api";
import logger from "../utils/logger";

/**
 * A custom hook to handle search logic
 * @param {string} searchQuery The current search query
 * @returns {object} An object containing search results, loading state and error state
 */

export function useSearch(searchQuery) {
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState(null);

  // Debounce the search query to avoid excessive API calls
  const debouncedSearchQuery = useDebounce(searchQuery, 500); // 500ms delay

  useEffect(() => {
    if (!debouncedSearchQuery) {
      setSearchResults([]);
      return;
    }

    const performSearch = async () => {
      setSearchLoading(true);
      setSearchError(null);

      try {
        const results = await apiFetch(
          `/parts/search/?q=${debouncedSearchQuery}`
        );
        setSearchResults(results);
      } catch (err) {
        setSearchError(err.message);
        logger.error("Failed to fetch search results:", err);
      } finally {
        setSearchLoading(false);
      }
    };

    performSearch();
  }, [debouncedSearchQuery]); // Effect runs when the debounced query changes

  return { searchResults, searchLoading, searchError };
}

export default useSearch;
