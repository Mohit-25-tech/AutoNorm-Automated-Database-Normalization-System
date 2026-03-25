import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            minHeight: "100vh",
            padding: "2rem",
            textAlign: "center",
            background: "var(--bg, #0a0c10)",
            color: "var(--text, #e2e8f0)",
            fontFamily: "'DM Sans', system-ui, sans-serif",
          }}
        >
          <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>⚠️</div>
          <h1 style={{ fontSize: "1.4rem", marginBottom: "0.5rem" }}>
            Something went wrong
          </h1>
          <p
            style={{
              color: "var(--text3, #4a5568)",
              fontSize: "0.9rem",
              maxWidth: "400px",
              marginBottom: "1.5rem",
            }}
          >
            An unexpected error occurred. Please try again.
          </p>
          <button
            onClick={this.handleReset}
            style={{
              background: "var(--accent, #00e5c0)",
              color: "#0a0c10",
              border: "none",
              borderRadius: "10px",
              padding: "0.75rem 1.5rem",
              fontWeight: 700,
              fontSize: "0.88rem",
              cursor: "pointer",
            }}
          >
            ↻ Reload App
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
