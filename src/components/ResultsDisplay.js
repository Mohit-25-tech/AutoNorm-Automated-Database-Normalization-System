import React, { useState } from "react";

const TABS = [
  { id: "keys", label: "Candidate Keys", icon: "🔑" },
  { id: "2nf", label: "2NF", icon: "②" },
  { id: "3nf", label: "3NF", icon: "③" },
  { id: "bcnf", label: "BCNF", icon: "◈" },
];

function StatusBadge({ ok }) {
  return (
    <span className={`status-badge ${ok ? "status-ok" : "status-fail"}`}>
      {ok ? "✓ Satisfied" : "✗ Violated"}
    </span>
  );
}

function TableCard({ table }) {
  return (
    <div className="table-card">
      <div className="table-card-header">
        <span className="table-name">{table.name}</span>
        <span className="table-pk-label">PK: {table.primary_key.join(", ") || "—"}</span>
      </div>
      <div className="table-attrs">
        {table.attributes.map((attr) => (
          <span
            key={attr}
            className={`attr-pill ${table.primary_key.includes(attr) ? "attr-pk" : ""}`}
          >
            {attr}
          </span>
        ))}
      </div>
    </div>
  );
}

function ViolationCard({ v }) {
  return (
    <div className="violation-card">
      <div className="violation-type">{v.type}</div>
      <div className="violation-fd">{v.fd}</div>
      <div className="violation-reason">{v.reason}</div>
    </div>
  );
}

export default function ResultsDisplay({ data }) {
  const [activeTab, setActiveTab] = useState("keys");

  if (!data) return null;

  const tabContent = {
    keys: (
      <div className="tab-content">
        <div className="result-block">
          <h3 className="block-title">Candidate Keys</h3>
          <div className="key-list">
            {data.candidate_keys.length === 0 ? (
              <p className="empty-note">No candidate keys found.</p>
            ) : (
              data.candidate_keys.map((key, i) => (
                <div key={i} className="key-row">
                  <span className="key-index">K{i + 1}</span>
                  <span className="key-value">{`{${key.join(", ")}}`}</span>
                </div>
              ))
            )}
          </div>
        </div>
        <div className="result-block">
          <h3 className="block-title">Prime Attributes</h3>
          <div className="attr-pills-row">
            {data.prime_attributes.length === 0 ? (
              <span className="empty-note">None</span>
            ) : (
              data.prime_attributes.map((a) => (
                <span key={a} className="attr-pill attr-pk">{a}</span>
              ))
            )}
          </div>
        </div>
        <div className="result-block">
          <h3 className="block-title">Non-Prime Attributes</h3>
          <div className="attr-pills-row">
            {data.candidate_keys.length > 0 &&
              (() => {
                const allAttrs = data.tables_bcnf.flatMap((t) => t.attributes);
                const unique = [...new Set(allAttrs)];
                const nonPrime = unique.filter((a) => !data.prime_attributes.includes(a));
                return nonPrime.length === 0 ? (
                  <span className="empty-note">None</span>
                ) : (
                  nonPrime.map((a) => <span key={a} className="attr-pill">{a}</span>)
                );
              })()}
          </div>
        </div>
      </div>
    ),
    "2nf": (
      <div className="tab-content">
        <div className="nf-header">
          <div>
            <h3 className="block-title">Second Normal Form (2NF)</h3>
            <p className="nf-desc">No non-prime attribute may be partially dependent on any candidate key.</p>
          </div>
          <StatusBadge ok={data.is_2nf} />
        </div>
        {!data.is_2nf && (
          <div className="result-block">
            <h4 className="sub-title">Violations Found</h4>
            {data.violations_2nf.map((v, i) => <ViolationCard key={i} v={v} />)}
          </div>
        )}
        <div className="result-block">
          <h4 className="sub-title">Resulting Tables</h4>
          {data.tables_2nf.map((t, i) => <TableCard key={i} table={t} />)}
        </div>
      </div>
    ),
    "3nf": (
      <div className="tab-content">
        <div className="nf-header">
          <div>
            <h3 className="block-title">Third Normal Form (3NF)</h3>
            <p className="nf-desc">For every FD X→Y, either X is a superkey or Y consists only of prime attributes.</p>
          </div>
          <StatusBadge ok={data.is_3nf} />
        </div>
        {!data.is_3nf && (
          <div className="result-block">
            <h4 className="sub-title">Violations Found</h4>
            {data.violations_3nf.map((v, i) => <ViolationCard key={i} v={v} />)}
          </div>
        )}
        <div className="result-block">
          <h4 className="sub-title">Resulting Tables</h4>
          {data.tables_3nf.map((t, i) => <TableCard key={i} table={t} />)}
        </div>
      </div>
    ),
    bcnf: (
      <div className="tab-content">
        <div className="nf-header">
          <div>
            <h3 className="block-title">Boyce-Codd Normal Form (BCNF)</h3>
            <p className="nf-desc">For every non-trivial FD X→Y, X must be a superkey.</p>
          </div>
          <StatusBadge ok={data.is_bcnf} />
        </div>
        {!data.is_bcnf && (
          <div className="result-block">
            <h4 className="sub-title">Violations Found</h4>
            {data.violations_bcnf.map((v, i) => <ViolationCard key={i} v={v} />)}
          </div>
        )}
        <div className="result-block">
          <h4 className="sub-title">Resulting Tables</h4>
          {data.tables_bcnf.map((t, i) => <TableCard key={i} table={t} />)}
        </div>
      </div>
    ),
  };

  return (
    <div className="results-display">
      <div className="results-header">
        <h2 className="results-title">Normalization Results</h2>
        <div className="nf-status-row">
          {["2NF", "3NF", "BCNF"].map((nf) => (
            <div key={nf} className={`nf-pill ${data[`is_${nf.toLowerCase()}`] ? "nf-ok" : "nf-fail"}`}>
              {nf} {data[`is_${nf.toLowerCase()}`] ? "✓" : "✗"}
            </div>
          ))}
        </div>
      </div>

      <div className="tabs">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? "tab-active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      <div className="tab-panel">{tabContent[activeTab]}</div>
    </div>
  );
}
