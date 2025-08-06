// src/components/ErrorBoundary.jsx
import React from "react";
import "./ErrorBoundary.css";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error to an error reporting service
    console.error("Uncaught error:", error, errorInfo);
    this.setState({ error, errorInfo });
  }

  render() {
    if (this.state.hasError) {
      // A user-friendly fallback UI.
      return (
        <div className="error-boundary">
          <div className="error-content">
            <h2>Oops! Something went wrong.</h2>
            <p>
              We're sorry for the inconvenience. Please try refreshing the page,
              or click the button below to return to the homepage.
            </p>
            <div className="error-actions">
              <button onClick={() => window.location.reload()}>
                Refresh Page
              </button>
              <a href="/" className="button">
                Go to Homepage
              </a>
            </div>
            {/* It can be helpful to show error details in development */}
            {import.meta.env.DEV && (
              <details style={{ marginTop: "20px", whiteSpace: "pre-wrap" }}>
                <summary>Error Details (for developers)</summary>
                {this.state.error && this.state.error.toString()}
                <br />
                {this.state.errorInfo && this.state.errorInfo.componentStack}
              </details>
            )}
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
