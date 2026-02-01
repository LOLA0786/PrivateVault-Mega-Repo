import { useEffect, useState } from "react";
import { api } from "../api";

export default function ReplayDrawer({ hash, onClose }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!hash) return;
    api.get(`/replay/${hash}`).then(r => setData(r.data));
  }, [hash]);

  if (!hash) return null;

  return (
    <div style={{
      position: "fixed",
      right: 0,
      top: 0,
      width: "40%",
      height: "100%",
      background: "#0b0b0b",
      borderLeft: "1px solid #222",
      padding: 16,
      color: "#ddd",
      overflow: "auto"
    }}>
      <button onClick={onClose}>Close</button>
      <pre style={{ fontSize: 12 }}>
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}
