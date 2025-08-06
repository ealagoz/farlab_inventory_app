// src/hooks/useDebounce.js
import { useState, useEffect } from "react";

/**
 * A custom hook to debounce a value
 * @param {any} value The value to debounce
 * @param {number} delay The debounce delay in milliseconds
 * @returns The debounced value.
 */
export function useDebounce(value, delay) {
  // State to store the debounced value
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // Clean up the timer if the value or delay changes, of if the component unmounts
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]); // Only re-run the effect if value or delay changes

  return debouncedValue;
}

export default useDebounce;
