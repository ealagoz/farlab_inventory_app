// PartsTable: Instrument Parts List
import React from "react";
import PartItem from "./PartItem";
import "./PartsTable.css";
import logger from "../utils/logger";

export function PartsTable({ parts, onEdit, onDelete, onStockChange }) {
  if (!parts) {
    logger.log(
      "PartsTable decision: parts prop is undefined or null. Rendering nothing."
    );
    return null;
  }

  if (!parts || parts.length === 0) {
    logger.log(
      "PartsTable decision: parts array is empty. Showing 'No parts found' message."
    );
    return (
      <p className="no-parts-message">No parts found for this instrument.</p>
    );
  }

  logger.log(`PartsTable decision: Rendering table with ${parts.length}parts.`);
  logger.log("------------------------------------");

  return (
    <div className="table-container">
      <table className="parts-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Part Number</th>
            <th>Name</th>
            <th>In Stock</th>
            <th>Status</th>
            <th>Manufacturer</th>
            <th>Actions</th>
            {/** Add Actions header */}
          </tr>
        </thead>
        <tbody>
          {parts.map((part, index) => (
            <PartItem
              key={part.id}
              part={part}
              index={index}
              onEdit={onEdit}
              onDelete={onDelete}
              onStockChange={onStockChange}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PartsTable;
