import { useEffect, useState } from "react";
import { api } from "../api";

export default function StatusBar() {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get("/status")
      .then(res => setStatus(res.data))
      .catch(err => setError(err.message));
  }, []);

  if (error) {
    return <div style={{ padding: 12, color: "red" }}>Error: {error}</div>;
  }

  if (!status) {
    return <div style={{ padding: 12, color: "#aaa" }}>Loading control plane…</div>;
  }

  return (
    <div style={{
      padding: "12px 16px",
      borderBottom: "1px solid #222",
      background: "#0b0b0b",
      color: "#eaeaea"
    }}>
      <div style={{ fontWeight: "bold", letterSpacing: "0.5px" }}>
        PRIVATEVAULT — SOVEREIGN CONTROL PLANE
      </div>
      <div style={{ fontSize: "13px", marginTop: "4px", opacity: 0.85 }}>
        Node: {status.node} | Mode: {status.mode.join(" + ")} | Policy: {status.policy_version}
      </div>
    </div>
  );
}
