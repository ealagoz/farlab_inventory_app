// src/pages/InstrumentPage.jsx
import React, { useState, useEffect, useCallback } from "react";
import { useParams } from "react-router-dom";
import { useAppContext } from "../context/AppContext";
import apiFetch from "../utils/api";
import logger from "../utils/logger";
import PartsTable from "../components/PartsTable";
import LoadingSpinner from "../components/LoadingSpinner";
import PartForm from "../components/PartForm";
import ConfirmDialog from "../components/ConfirmDialog";
import "./InstrumentPage.css";

export function InstrumentPage() {
  const { instrumentType } = useParams();
  const { instruments, instrumentsLoading, refreshAlertData } = useAppContext();
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // State for managing the form modal
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingPart, setEditingPart] = useState(null); // null for 'add', part object for 'edit'
  const [currentInstrumentId, setCurrentInstrumentId] = useState(null);

  // Delete confirmation dialog
  const [confirmDialog, setConfirmDialog] = useState({
    isOpen: false,
    title: "",
    message: "",
    onConfirm: null,
  });

  // Reusable fetch logic
  // Wrap fetchParts in useCallback so it can be called from other functions
  // without causing infinite loops in useEffect
  const fetchParts = useCallback(
    async (instrumentId) => {
      if (!instrumentId) return;

      try {
        logger.log(`Starting to fetch parts for instrument ID: 
      ${instrumentId}`);
        const data = await apiFetch(
          `/api/parts/?instrument_id=${instrumentId}`
        );
        logger.log("Successfully fetched parts:", data);

        // Ensure data is array
        if (Array.isArray(data)) {
          setParts(data || []);
        } else {
          logger.warn(
            "API response for parts was not an array. Defaulting to []."
          );
          setParts([]);
        }
        setError(null); // Clear previous errors on a successfull fetch
      } catch (err) {
        logger.error(`Failed to fetch parts for ${instrumentType}:`, err);
        setError(err.message);
      } finally {
        logger.log("Calling setLoading(false) in finally block.");
        setLoading(false);
      }
    },
    [instrumentType]
  ); // instrumentType to dependency array for corretness.

  // This useEffect the instrument and triggers the initial fetch.
  useEffect(() => {
    logger.log(`==> useEffect triggered for [${instrumentType}]`);
    logger.log(`useEffect State: instrumentsLoading=
      ${instrumentsLoading}, instruments.length=${instruments.length}`);

    if (instrumentsLoading) {
      return; // Wait for the main instrument list to load
    }

    // Handle case where no instrument exists in db
    if (instruments.length === 0) {
      logger.log(
        "useEffect Guard 2: Aborting because instrument list is empty."
      );
      setError("No instruments have been added to the database yet.");
      setLoading(false);
      return;
    }

    const currentInstrument = instruments.find(
      (inst) => inst.name.toLowerCase() === instrumentType.toLowerCase()
    );

    if (currentInstrument) {
      setCurrentInstrumentId(currentInstrument.id);
      fetchParts(currentInstrument.id); // Call the fetch function
    } else {
      logger.log(`useEffect Guard 3: Instrument "${instrumentType}" not
      found in the list.`);
      setError(`Instrument type "${instrumentType}" not found.`);
      setLoading(false);
      return;
    }

    // Store the instrument ID ==================>>>>>>>>>>>>>>>>>
    setCurrentInstrumentId(currentInstrument.id);
    logger.log(`Found current instrument:`, currentInstrument);

    // This effect should re-run when the instrumentType (from URL) or the
    // main instrument list changes
  }, [instrumentType, instruments, instrumentsLoading, fetchParts]);

  // -- Handlers for delete confirm dialog --
  const showConfirmDialog = (title, message, onConfirm) => {
    setConfirmDialog({
      isOpen: true,
      title,
      message,
      onConfirm,
    });
  };

  const hideConfirmDialog = () => {
    setConfirmDialog({
      isOpen: false,
      title: "",
      message: "",
      onConfirm: null,
    });
  };

  // --- Handlers for CRUD operations ---
  const handleAddPart = () => {
    setEditingPart(null); // Ensure it is in 'add' mode
    setIsFormOpen(true);
  };

  const handleEditPart = (part) => {
    setEditingPart(part); // Set the part to edit
    setIsFormOpen(true);
  };

  const handleDeletePart = useCallback(
    async (partId) => {
      // Ask for confirmation before deleting
      showConfirmDialog(
        "Delete Part",
        "Are you sure you want to delete this part? This action cannot be undone."
      );
      try {
        // Assumes backend is set up to handle DELETE /api/parts/:id
        await apiFetch(`/api/parts/${partId}`, { method: "DELETE" });
        // Refetch after a successfull delete
        fetchParts(currentInstrumentId);
        refreshAlertData?.(); // Refresh alerts on delete
      } catch (err) {
        logger.error("Failed to delete part:", err);
        setError(err.message);
      } finally {
        hideConfirmDialog(); // ensure dialog is closed if needed
      }
    },
    [
      currentInstrumentId,
      fetchParts,
      refreshAlertData,
      showConfirmDialog,
      apiFetch,
      logger,
      setError,
      hideConfirmDialog,
    ]
  );

  const handleSavePart = useCallback(
    async (formData) => {
      // Debugging logs
      logger.log("Attempting to save part. Form data: ", formData);
      logger.log("Current part being edited:", editingPart);
      // Prepare a clean payload for the API, ensuring correct data types.
      const payload = {
        ...formData,
        // Use instrument_ids from formData if provided, otherwise use current instrument
        instrument_ids:
          formData.instrument_ids && formData.instrument_ids.length > 0
            ? formData.instrument_ids
            : [currentInstrumentId],
        quantity_in_stock: parseInt(formData.quantity_in_stock || "0", 10),
        minimum_stock_level: parseInt(formData.minimum_stock_level || "0", 10),
        is_critical: formData.is_critical || false,
        instrument_id: currentInstrumentId,
      };
      try {
        if (editingPart) {
          // UPDATE (PATCH request)
          // Assumes backend is set up to handle PUT /api/parts/:id
          await apiFetch(`/api/parts/${editingPart.id}`, {
            method: "PATCH",
            body: JSON.stringify(payload),
          });
        } else {
          // CREATE (POST request)
          // Assumes backend is set up to handle POST /api/parts/
          await apiFetch(`/api/parts/`, {
            method: "POST",
            body: JSON.stringify(payload),
          });
        }
        // Close the form on successful save
        setIsFormOpen(false);
        // After a successfull save, refetch all parts for this instrument
        // This guarantees the UI will show the latest data from the server
        fetchParts(currentInstrumentId);
        if (refreshAlertData) refreshAlertData();
        setError(null);
      } catch (err) {
        logger.error("Failed to save part:", err);
        setError(err.message);
      }
    },
    [currentInstrumentId, editingPart, fetchParts, refreshAlertData]
  );

  const handleCancelForm = () => {
    setIsFormOpen(false);
    setEditingPart(null); // Reset editing state on cancel.
  };

  const handleStockChange = useCallback(
    async (part, newQuantity) => {
      // Ensure the new quantity is NOT negative
      if (part.quantity_in_stock + newQuantity < 0) {
        return;
      }

      try {
        logger.log("Debug - part.quantity_in_stock:", part.quantity_in_stock);
        logger.log("Debug - newQuantity:", newQuantity);
        const updatedPartFromServer = await apiFetch(
          `/api/parts/${part.id}/stock`,
          {
            method: "POST", // Changed from "PATCH"
            body: JSON.stringify({
              quantity_change: newQuantity, // Changed from quantity_in_stock to quantity_change
              reason: "Stock adjustment via UI", // Optional reason field
            }),
          }
        );

        // Refetch only quantity_in_stock parameter
        setParts((currentParts) =>
          currentParts.map((p) =>
            p.id === updatedPartFromServer.id ? updatedPartFromServer : p
          )
        );
        // Refresh alert data here
        if (refreshAlertData) refreshAlertData();
        // Cear any previous errors on success.
        setError(null);
      } catch (err) {
        logger.error("Failed to update stock:", err);
        setError("Failed to update stock. Reverting changes.");
      }
    },
    [refreshAlertData]
  );

  logger.log("--- Preparing to render ---");
  if (instrumentsLoading || loading) {
    logger.log("Render decision: SHOWING SPINNER");
  } else if (error) {
    logger.log("Render decision: SHOWING ERROR -", error);
  } else {
    logger.log(
      "Render decision: SHOWING PARTS TABLE with",
      parts.length,
      "parts"
    );
  }
  logger.log("-------------------------------------------------");

  if (instrumentsLoading || loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <div className="error-message">Error: {error}</div>;
  }

  return (
    <div className="instrument-page">
      <div className="page-header">
        {/* <h1>{instrumentType.toUpperCase()} Inventory</h1> */}
        <button className="add-part-btn" onClick={handleAddPart}>
          + Add New Part
        </button>
      </div>
      {/* Display any error messages here */}
      {error && <div className="error-message">Error: {error}</div>}
      {Array.isArray(parts) && (
        <PartsTable
          parts={parts}
          onEdit={handleEditPart}
          onDelete={handleDeletePart}
          onStockChange={handleStockChange}
        />
      )}
      {/** Conditionally render the form modal */}
      {isFormOpen && (
        <PartForm
          key={editingPart ? editingPart.id : "new-part-form"}
          part={editingPart}
          onSave={handleSavePart}
          onCancel={handleCancelForm}
          instrumentId={currentInstrumentId}
          availableInstruments={instruments}
        />
      )}
      <ConfirmDialog
        isOpen={confirmDialog.isOpen}
        title={confirmDialog.title}
        message={confirmDialog.message}
        onConfirm={confirmDialog.onConfirm}
        onCancel={hideConfirmDialog}
      />
    </div>
  );
}

export default InstrumentPage;
