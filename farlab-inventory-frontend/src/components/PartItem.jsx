// PartItem: Individual Part Row Display
import React from "react";
import "./PartItem.css";
import logger from "../utils/logger";
import { getStatusClass } from "../utils/styleUtils";

export function PartItem({ part, index, onEdit, onDelete, onStockChange }) {
  // Receive handleDecrement, onEdit and onDelete functions
  const handleEditClick = () => {
    onEdit(part); // Pass the entire part object up
  };
  const handleDeleteClick = () => {
    onDelete(part.id); // Pass the part's ID up
  };
  const handleIncrement = () => {
    onStockChange(part, part.quantity_in_stock + 1);
  };
  const handleDecrement = () => {
    onStockChange(part, part.quantity_in_stock - 1);
  };

  return (
    <tr className="part-item">
      <td>{index + 1}</td>
      <td>{part.part_number || "N/A"}</td>
      <td>{part.name}</td>
      <td className="stock-cell">
        <button className="stock-btn btn-decrement" onClick={handleDecrement}>
          -
        </button>
        <span className="stock-quantity">{part.quantity_in_stock}</span>
        <button className="stock-btn btn-increment" onClick={handleIncrement}>
          +
        </button>
      </td>
      <td>
        <span className={`status-badge ${getStatusClass(part.stock_status)}`}>
          {part.stock_status}
        </span>
      </td>
      <td>{part.manufacturer || "N/A"}</td>
      <td className="actions-cell">
        <button className="btn-edit" onClick={handleEditClick}>
          Edit
        </button>
        <button className="btn-delete" onClick={handleDeleteClick}>
          Delete
        </button>
      </td>
    </tr>
  );
}

export default PartItem;
