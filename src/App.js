import React, { useState, useEffect } from "react";
import SchemaInput from "./components/SchemaInput";
import ResultsDisplay from "./components/ResultsDisplay";
import "./App.css";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");
  const [theme, setTheme] = useState("dark");
  const [fontStyle, setFontStyle] = useState("modern");

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  useEffect(() => {
    document.documentElement.dataset.font = fontStyle;
  }, [fontStyle]);

  const handleNormalize = async (payload) => {
    setLoading(true);
    setApiError("");
    setResults(null);
    try {
      const res = await fetch(`${API_URL}/normalize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Server error");
      }
      const data = await res.json();
      setResults(data);
    } catch (e) {
      setApiError(e.message || "Failed to connect to backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-inner">
          <div className="header-left">
            <div className="logo-mark">⬡</div>
            <div>
              <h1 className="app-title">AutoNorm</h1>
              <p className="app-subtitle">A Step-by-Step Relational Database Normalizer</p>
            </div>
          </div>
          <div className="header-controls">
            <div className="control-group">
              <span className="control-label">Theme</span>
              <div className="control-toggle">
                <button
                  type="button"
                  className={`toggle-btn ${theme === "dark" ? "toggle-active" : ""}`}
                  onClick={() => setTheme("dark")}
                >
                  Dark
                </button>
                <button
                  type="button"
                  className={`toggle-btn ${theme === "light" ? "toggle-active" : ""}`}
                  onClick={() => setTheme("light")}
                >
                  Light
                </button>
              </div>
            </div>
            <div className="control-group">
              <span className="control-label">Font</span>
              <select
                className="control-select"
                value={fontStyle}
                onChange={(e) => setFontStyle(e.target.value)}
              >
                <option value="modern">Modern Sans</option>
                <option value="mono">Technical Mono</option>
                <option value="playful">Playful Rounded</option>
              </select>
            </div>
          </div>
        </div>
      </header>

      <main className="app-main">
        <div className="layout">
          <div className="panel panel-left">
            <SchemaInput onSubmit={handleNormalize} loading={loading} />
          </div>
          <div className="panel panel-right">
            {apiError && (
              <div className="api-error">
                <strong>Error:</strong> {apiError}
              </div>
            )}
            {!results && !apiError && (
              <div className="empty-state">
                <div className="empty-icon">◈</div>
                <p className="empty-title">Ready to Normalize</p>
                <p className="empty-desc">Define your schema on the left, then click "Normalize Schema" to see the step-by-step decomposition.</p>
              </div>
            )}
            {results && <ResultsDisplay data={results} />}
          </div>
        </div>
      </main>
    </div>
  );
}
