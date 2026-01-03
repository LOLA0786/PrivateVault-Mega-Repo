import { useEffect, useState } from "react";
import { api } from "../api";

export default function ShadowImpactPanel() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get("/shadow/summary")
      .then(r => setData(r.data))
      .catch(() => setData({
        would_block: 0,
        exposure_prevented: 0,
        violations: []
      }));
  }, []);

  if (!data) {
    return (
      <div style={{
        width: 300,
        padding: 16,
        borderLeft: "1px solid #222",
        color: "#aaa"
      }}>
        Loading shadow impact…
      </div>
    );
  }

  return (
    <div style={{
      width: 300,
      padding: 16,
      borderLeft: "1px solid #222",
      background: "#0b0b0b",
      color: "#ddd"
    }}>
      <h3 style={{ marginBottom: 12 }}>Shadow Impact</h3>

      <div style={{ marginBottom: 12 }}>
        <strong>Would Block</strong>
        <div style={{ fontSize: 24 }}>{data.would_block}</div>
      </div>

      <div style={{ marginBottom: 12 }}>
        <strong>Exposure Prevented</strong>
        <div style={{ fontSize: 18 }}>₹ {data.exposure_prevented}</div>
      </div>

      <div>
        <strong>Violations</strong>
        <ul style={{ paddingLeft: 18 }}>
          {(data.violations && data.violations.length > 0)
            ? data.violations.map((v, i) => <li key={i}>{v}</li>)
            : <li>None</li>
          }
        </ul>
      </div>
    </div>
  );
}
