import React, { useEffect, useRef } from "react";
import PropTypes from "prop-types";
import "./ConfirmDialog.css";

export const ConfirmDialog = ({
  isOpen,
  title,
  message,
  onConfirm,
  onCancel,
}) => {
  const dialogRef = useRef(null);
  const cancelButtonRef = useRef(null);

  // Handle keyboard interactions and focus management
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onCancel();
      }
    };

    // Focus the cancel button when dialog opens
    if (cancelButtonRef.current) {
      cancelButtonRef.current.focus();
    }

    // Add event listener
    document.addEventListener("keydown", handleKeyDown);

    // Prevent body scroll when modal is open
    document.body.style.overflow = "hidden";

    // Cleanup
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "unset";
    };
  }, [isOpen, onCancel]);

  if (!isOpen) return null;

  return (
    // Use a semantic backdrop - no interactive div
    <div className="confirm-dialog-overlay">
      <div
        ref={dialogRef}
        className="confirm-dialog-content"
        aria-modal="true"
        aria-labelledby="dialog-title"
        aria-describedby="dialog-message"
      >
        <h3 id="dialog-title" className="confirm-dialog-title">
          {title}
        </h3>
        <p id="dialog-message" className="confirm-dialog-message">
          {message}
        </p>
        <div className="confirm-dialog-actions">
          <button
            ref={cancelButtonRef}
            onClick={onCancel}
            className="btn-cancel"
            type="button"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="btn-confirm btn-danger"
            type="button"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
};

ConfirmDialog.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  title: PropTypes.string.isRequired,
  message: PropTypes.string.isRequired,
  onConfirm: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
};

export default ConfirmDialog;
