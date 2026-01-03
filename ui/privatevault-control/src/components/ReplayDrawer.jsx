import { useEffect, useState } from "react";
import { api } from "../api";

export default function ReplayDrawer({ intentHash, onClose }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!intentHash) return;
    api.get(`/replay/${intentHash}`).then(res => setData(res.data));
  }, [intentHash]);

  if (!intentHash) return null;

  return (
    <div style={{
      position: "fixed",
      top: 0,
      right: 0,
      width: "40%",
      height: "100%",
      background: "#0b0b0b",
      borderLeft: "1px solid #222",
      padding: "16px",
      color: "#ddd",
      overflow: "auto"
    }}>
      <button onClick={onClose} style={{ marginBottom: 12 }}>Close</button>
      <h3>Intent Replay</h3>
      <pre style={{ fontSize: "12px", whiteSpace: "pre-wrap" }}>
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}
