// src/utils/styleUtils.js

/**
 * Returns the appropriate CSS class for a given part stock status.
 * @param {string} status - The stock status string (e.g., "In stock", "Low stock").
 * @returns {string} The corresponding CSS class name
 */
export const getStatusClass = (status) => {
  if (!status) return "";
  const lowerCaseStatus = status.toLowerCase();
  if (lowerCaseStatus.includes("in stock")) return "status-in";
  if (lowerCaseStatus.includes("low stock")) return "status-low";
  if (lowerCaseStatus.includes("out of stock")) return "status-out";
  return "";
};
