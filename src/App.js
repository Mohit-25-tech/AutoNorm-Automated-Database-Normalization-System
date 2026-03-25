import React, { useState, useEffect } from "react";
import SchemaInput from "./components/SchemaInput";
import ResultsDisplay from "./components/ResultsDisplay";
import ErrorBoundary from "./components/ErrorBoundary";
import "./App.css";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";
const FETCH_TIMEOUT_MS = 30000; // 30 seconds

export default function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");
  const [theme, setTheme] = useState("dark");
  const [fontStyle, setFontStyle] = useState("modern");
  /** 'input' = schema form; 'results' = normalization output */
  const [page, setPage] = useState("input");
  /** Increment to remount SchemaInput and clear its internal state on reset */
  const [formKey, setFormKey] = useState(0);

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

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);

    try {
      const res = await fetch(`${API_URL}/normalize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      if (!res.ok) {
        let detail = "Server error";
        try {
          const err = await res.json();
          detail = err.detail || detail;
        } catch {
          // response wasn't JSON
        }
        throw new Error(detail);
      }
      const data = await res.json();
      setResults(data);
      setPage("results");
    } catch (e) {
      if (e.name === "AbortError") {
        setApiError("Request timed out. The schema may be too complex — try fewer attributes.");
      } else if (e.message === "Failed to fetch") {
        setApiError("Cannot connect to the backend server. Please check if it is running.");
      } else {
        setApiError(e.message || "Failed to connect to backend.");
      }
    } finally {
      clearTimeout(timeoutId);
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResults(null);
    setApiError("");
    setPage("input");
    setFormKey((k) => k + 1);
  };

  return (
    <ErrorBoundary>
      <div className="app">
        <header className="app-header">
          <div className="header-inner">
            <div className="header-left header-left-compact">
              <div className="logo-mark">⬡</div>
              <span className="header-brand-short">AutoNorm</span>
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
          {page === "input" && (
            <div className="page page-input">
              <div className="input-hero">
                <h1 className="app-title page-title">AutoNorm</h1>
                <p className="app-subtitle page-subtitle">
                  A Step-by-Step Relational Database Normalizer
                </p>
              </div>
              <div className="panel panel-full">
                {apiError && (
                  <div className="api-error api-error-inline">
                    <strong>Error:</strong> {apiError}
                  </div>
                )}
                <SchemaInput
                  key={formKey}
                  onSubmit={handleNormalize}
                  loading={loading}
                />
              </div>
            </div>
          )}

          {page === "results" && results && (
            <div className="page page-results">
              <div className="panel panel-full panel-results">
                <ResultsDisplay data={results} onReset={handleReset} />
              </div>
            </div>
          )}
        </main>
      </div>
    </ErrorBoundary>
  );
}
