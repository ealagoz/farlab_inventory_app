// src/components/PartForm.jsx
import React, { useState, useEffect } from "react";
import "./PartForm.css";
import logger from "../utils/logger";

function PartForm({ part, onSave, onCancel, instrumentId }) {
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
    } else {
      // Reset the form to its initial, clean state
      setFormData(getInitialState());
    }
  }, [part, instrumentId]); // Rerun this logic when the part to edit changes.

  // This function handles changes for all form inputs
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault(); // Prevent default browser form submission.
    logger.log("Submitting form data:", formData);
    // The onSave function will handle both creating and updating
    onSave(formData);
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
