import { useEffect, useState } from "react";
import { api } from "../api";
import ReplayDrawer from "./ReplayDrawer";

export default function IntentTable() {
  const [intents, setIntents] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    api.get("/intents/recent")
      .then(res => setIntents(res.data))
      .catch(() => setIntents([]));
  }, []);

  return (
    <div style={{ padding: "16px", color: "#ddd" }}>
      <h3 style={{ marginBottom: "8px" }}>Live Intent Stream</h3>

      <table width="100%" cellPadding="6" style={{ borderCollapse: "collapse", fontSize: "13px" }}>
        <thead>
          <tr style={{ borderBottom: "1px solid #333", color: "#aaa" }}>
            <th align="left">Time</th>
            <th align="left">Domain</th>
            <th align="left">Actor</th>
            <th align="left">Action</th>
            <th align="left">Decision</th>
            <th align="left">Replay</th>
          </tr>
        </thead>
        <tbody>
          {intents.map((i, idx) => (
            <tr key={idx} style={{ borderBottom: "1px solid #222" }}>
              <td>{i.timestamp.slice(11, 19)}</td>
              <td>{i.domain}</td>
              <td>{i.actor}</td>
              <td>{i.action}</td>
              <td>{i.decision}</td>
              <td>
                <button onClick={() => setSelected(i.intent_hash)}>
                  {i.intent_hash.slice(0, 10)}…
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <ReplayDrawer
        intentHash={selected}
        onClose={() => setSelected(null)}
      />
    </div>
  );
}
