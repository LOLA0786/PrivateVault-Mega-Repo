import { useEffect, useState } from "react";
import { api } from "../api";

export default function ShadowImpactPanel() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get("/shadow/summary").then(r => setData(r.data));
  }, []);

  if (!data) return <div style={{ padding: 16 }}>Loading shadow impact…</div>;

  return (
    <div style={{
      width: 300,
      padding: 16,
      borderLeft: "1px solid #222",
      background: "#0b0b0b"
    }}>
      <h3>Shadow Impact</h3>
      <div><strong>Would Block:</strong> {data.would_block ?? 0}</div>
      <div><strong>Exposure Prevented:</strong> ₹ {data.exposure_prevented ?? 0}</div>
      <div><strong>Violations:</strong></div>
      <ul>
        {(data.violations?.length ? data.violations : ["None"]).map((v,i) =>
          <li key={i}>{v}</li>
        )}
      </ul>
    </div>
  );
}
