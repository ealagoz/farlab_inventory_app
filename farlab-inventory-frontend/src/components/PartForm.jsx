// src/components/PartForm.jsx
import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

import "./PartForm.css";
import logger from "../utils/logger";

function PartForm({
  part,
  onSave,
  onCancel,
  instrumentId,
  availableInstruments = [],
}) {
  // This function ensures clean state for the form.
  const getInitialState = () => ({
    part_number: "",
    name: "",
    quantity_in_stock: "",
    minimum_stock_level: "",
    stock_status: "",
    manufacturer: "",
    instrument_id: "",
  });
  const [formData, setFormData] = useState(getInitialState());
  const [selectedInstruments, setSelectedInstruments] = useState([]);

  useEffect(() => {
    // If a 'part' prop is passed, it means we are editing.
    // Pre-fill the form with the part's data.
    if (part) {
      setFormData({
        ...part, // Keep all original fields from the part object
        // Explicitly ensure fields bound to inputs are defined strings.
        part_number: part.part_number || "",
        name: part.name || "",
        quantity_in_stock: part.quantity_in_stock || "",
        minimum_stock_level: part.minimum_stock_level || "",
        stock_status: part.stock_status || "",
        manufacturer: part.manufacturer || "",
        instrument_id: part.instrument_id || "",
      });

      if (part.instruments && Array.isArray(part.instruments)) {
        const instrumentIds = part.instruments.map((inst) => inst.id);
        setSelectedInstruments(instrumentIds);
      } else {
        setFormData(getInitialState());
        if (instrumentId) {
          setSelectedInstruments([instrumentId]);
        } else {
          setSelectedInstruments([]);
        }
      }
    } else {
      // Reset the form to its initial, clean state
      setFormData(getInitialState());
    }
  }, [part, instrumentId, availableInstruments]); // Rerun this logic when the part to edit changes.

  // This function handles changes for all form inputs
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  // This function handles instrument selection
  const handleInstrumentSelection = (instrumentId, isChecked) => {
    setSelectedInstruments((prevSelected) => {
      if (isChecked) {
        return [...prevSelected, instrumentId];
      } else {
        return prevSelected.filter((id) => id != instrumentId);
      }
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault(); // Prevent default browser form submission.

    let instrumentIds = [];

    if (selectedInstruments.length > 0) {
      instrumentIds = selectedInstruments;
    } else if (instrumentId) {
      instrumentIds = [instrumentId];
    }

    const payload = {
      ...formData,
      instrument_ids: instrumentIds,
    };

    logger.log("Submitting form data:", payload);
    // The onSave function will handle both creating and updating
    onSave(payload);
  };

  return (
    <div className="part-form-modal">
      <div className="part-form-content">
        <h2>{part ? "Edit Part" : "Add New Part"}</h2>
        <form onSubmit={handleSubmit}>
          {/** Each input MUST have both 'value' and 'onChange' */}
          <div className="form-group">
            <label htmlFor="part-number">Part Number</label>
            <input
              type="text"
              id="part_number"
              name="part_number"
              value={formData.part_number}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="name">Name</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="quantity_in_stock">In Stock</label>
            <input
              type="number"
              id="quantity_in_stock"
              name="quantity_in_stock"
              value={formData.quantity_in_stock}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="minimum_stock_level">Minimum Stock</label>
            <input
              type="number"
              id="minimum_stock_level"
              name="minimum_stock_level"
              value={formData.minimum_stock_level}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="stock_status">Status</label>
            <select
              id="stock_status"
              name="stock_status"
              value={formData.stock_status}
              onChange={handleChange}
              required
            >
              <option value="">Select Status</option>
              <option value="New">New</option>
              <option value="Used">Used</option>
              <option value="Refurbished">Refurbished</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="manufacturer">Manufacturer</label>
            <input
              type="text"
              id="manufacturer"
              name="manufacturer"
              value={formData.manufacturer}
              onChange={handleChange}
              required
            />
          </div>
          {availableInstruments && availableInstruments.length > 0 && (
            <div className="form-group">
              <label htmlFor="Instruments">Associate with Instruments:</label>
              <div className="instrument-checkboxes">
                {availableInstruments.map((instrument) => (
                  <label key={instrument.id} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={selectedInstruments.includes(instrument.id)}
                      onChange={(e) =>
                        handleInstrumentSelection(
                          instrument.id,
                          e.target.checked
                        )
                      }
                    />
                    <span className="instrument-name">{instrument.name}</span>
                  </label>
                ))}
              </div>
            </div>
          )}
          <div className="form-actions">
            <button type="submit" className="btn-save" onClick={handleSubmit}>
              Save
            </button>
            <button type="button" className="btn-cancel" onClick={onCancel}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default PartForm;

// Props validations
PartForm.propTypes = {
  part: PropTypes.shape({
    part_number: PropTypes.string,
    name: PropTypes.string,
    quantity_in_stock: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.number,
    ]),
    minimum_stock_level: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.number,
    ]),
    stock_status: PropTypes.string,
    manufacturer: PropTypes.string,
    instrument_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    instruments: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
          .isRequired,
      })
    ),
  }),
  onSave: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  instrumentId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  availableInstruments: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    })
  ),
};
