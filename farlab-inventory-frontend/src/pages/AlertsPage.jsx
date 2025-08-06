import React from "react";
import LoadingSpinner from "../components/LoadingSpinner";
import "./AlertsPage.css";
import { useAppContext } from "../context/AppContext";

const AlertsPage = () => {
  const { activeAlerts, alertSummary, alertsLoading, alertsError } =
    useAppContext();

  if (alertsLoading) {
    return <LoadingSpinner />;
  }

  if (alertsError) {
    return <div className="alert-error">Error: {alertsError}</div>;
  }

  return (
    <div className="alerts-page">
      <h1>Inventory Alerts</h1>
      {alertSummary && (
        <div className="alert-summary">
          <h2>Summary</h2>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="summary-value">{alertSummary.total_alerts}</span>
              <span className="summary-label">Total Alerts</span>
            </div>
            <div className="summary-item active">
              <span className="summary-value">
                {alertSummary.active_alerts}
              </span>
              <span className="summary-label">Active Alerts</span>
            </div>
            <div className="summary-item critical">
              <span className="summary-value">
                {alertSummary.critical_parts_low}
              </span>
              <span className="summary-label">Critical Parts Low</span>
            </div>
            <div className="summary-item out-of-stock">
              <span className="summary-value">
                {alertSummary.out_of_stock_parts}
              </span>
              <span className="summary-labe">Out of Stock</span>
            </div>
          </div>
        </div>
      )}
      <div className="alert-list">
        <h2>Active Low Stock Alerts</h2>
        {activeAlerts.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>Part ID</th>
                <th>Message</th>
                <th>Current Stock</th>
                <th>Threshold</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {activeAlerts.map((alert) => (
                <tr key={alert.id}>
                  <td>{alert.part_id}</td>
                  <td>{alert.message}</td>
                  <td>{alert.current_stock}</td>
                  <td>{alert.threshold_stock}</td>
                  <td>{new Date(alert.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No active alerts.</p>
        )}
      </div>
    </div>
  );
};

export default AlertsPage;
