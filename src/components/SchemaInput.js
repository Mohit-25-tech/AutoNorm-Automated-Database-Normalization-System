import React, { useState } from "react";

export default function SchemaInput({ onSubmit, loading }) {
  const [attrInput, setAttrInput] = useState("");
  const [attributes, setAttributes] = useState([]);
  const [fds, setFds] = useState([{ lhs: "", rhs: "" }]);
  const [error, setError] = useState("");

  const addAttribute = () => {
    const trimmed = attrInput.trim().toUpperCase();
    if (!trimmed) return;
    if (attributes.includes(trimmed)) {
      setError(`Attribute "${trimmed}" already exists.`);
      return;
    }
    setAttributes([...attributes, trimmed]);
    setAttrInput("");
    setError("");
  };

  const removeAttribute = (attr) => {
    setAttributes(attributes.filter((a) => a !== attr));
  };

  const handleAttrKeyDown = (e) => {
    if (e.key === "Enter") { e.preventDefault(); addAttribute(); }
  };

  const updateFd = (index, field, value) => {
    const updated = [...fds];
    updated[index][field] = value.toUpperCase();
    setFds(updated);
  };

  const addFd = () => setFds([...fds, { lhs: "", rhs: "" }]);

  const removeFd = (index) => setFds(fds.filter((_, i) => i !== index));

  const parseFdSide = (str) =>
    str.split(",").map((s) => s.trim()).filter((s) => s.length > 0);

  const handleSubmit = () => {
    setError("");
    if (attributes.length < 2) {
      setError("Please add at least 2 attributes.");
      return;
    }
    const validFds = fds.filter((fd) => fd.lhs.trim() && fd.rhs.trim());
    if (validFds.length === 0) {
      setError("Please add at least one complete functional dependency.");
      return;
    }
    for (const fd of validFds) {
      const lhsAttrs = parseFdSide(fd.lhs);
      const rhsAttrs = parseFdSide(fd.rhs);
      const allValid = [...lhsAttrs, ...rhsAttrs].every((a) => attributes.includes(a));
      if (!allValid) {
        setError(`FD "${fd.lhs} → ${fd.rhs}" contains attributes not in your schema.`);
        return;
      }
    }
    onSubmit({
      attributes,
      functional_dependencies: validFds.map((fd) => ({
        lhs: parseFdSide(fd.lhs),
        rhs: parseFdSide(fd.rhs),
      })),
    });
  };

  return (
    <div className="schema-input">
      <section className="input-section">
        <h2 className="section-title">
          <span className="step-badge">01</span>
          Define Attributes
        </h2>
        <div className="attr-input-row">
          <input
            className="text-input"
            type="text"
            placeholder="e.g. A, StudentID, CourseCode..."
            value={attrInput}
            onChange={(e) => setAttrInput(e.target.value)}
            onKeyDown={handleAttrKeyDown}
          />
          <button className="btn-add" onClick={addAttribute}>Add</button>
        </div>
        <div className="attr-chips">
          {attributes.length === 0 && (
            <span className="placeholder-text">No attributes yet — add some above</span>
          )}
          {attributes.map((attr) => (
            <span key={attr} className="chip">
              {attr}
              <button className="chip-remove" onClick={() => removeAttribute(attr)}>×</button>
            </span>
          ))}
        </div>
      </section>

      <section className="input-section">
        <h2 className="section-title">
          <span className="step-badge">02</span>
          Functional Dependencies
        </h2>
        <p className="hint-text">Use comma-separated attribute names. e.g. LHS: <code>A, B</code> → RHS: <code>C</code></p>
        <div className="fd-list">
          {fds.map((fd, i) => (
            <div key={i} className="fd-row">
              <input
                className="text-input fd-input"
                placeholder="LHS (e.g. A, B)"
                value={fd.lhs}
                onChange={(e) => updateFd(i, "lhs", e.target.value)}
              />
              <span className="arrow-symbol">→</span>
              <input
                className="text-input fd-input"
                placeholder="RHS (e.g. C)"
                value={fd.rhs}
                onChange={(e) => updateFd(i, "rhs", e.target.value)}
              />
              {fds.length > 1 && (
                <button className="btn-remove" onClick={() => removeFd(i)}>✕</button>
              )}
            </div>
          ))}
        </div>
        <button className="btn-secondary" onClick={addFd}>+ Add Dependency</button>
      </section>

      {error && <div className="error-banner">{error}</div>}

      <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
        {loading ? (
          <span className="loading-text"><span className="spinner" />Analyzing...</span>
        ) : (
          "⚡ Normalize Schema"
        )}
      </button>
    </div>
  );
}
