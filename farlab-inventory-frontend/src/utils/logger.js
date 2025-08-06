// src/utils/logger.js
// Centralized switch for all loging
// Reads from the .env file. Defaults to 'false' if not set.

const LOGGING_ENABLED = import.meta.env.VITE_LOGGING_ENABLED === "true";

/**
 * A simple logger utitility that can be globally enabled or disabled.
 * IT wraps the native console object.
 */
const logger = {
  /**
   * Logs a standard message.
   * @param {...any} args - Arguments to log.
   */
  log: (...args) => {
    if (LOGGING_ENABLED) {
      console.log(...args);
    }
  },
  /**
   * Logs awarning message.
   * @param {...any} args - Arguments to log.
   */
  warn: (...args) => {
    if (LOGGING_ENABLED) {
      console.warn(...args);
    }
  },
  /**
   * Logs a table.
   * @param {any} data - The data to display in a table.
   */
  table: (data) => {
    if (LOGGING_ENABLED) {
      console.table(data);
    }
  },
  /**
   * Logs an error message
   * @param {...any} args - Errors to log
   */
  error: (...args) => {
    if (LOGGING_ENABLED) {
      console.error(...args);
    }
  },
};

export default logger;
