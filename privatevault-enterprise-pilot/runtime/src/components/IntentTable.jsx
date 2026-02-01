import { useEffect, useState } from "react";
import { api } from "../api";
import ReplayDrawer from "./ReplayDrawer";

export default function IntentTable() {
  const [intents, setIntents] = useState([]);
  const [open, setOpen] = useState(null);

  useEffect(() => {
    api.get("/intents/recent").then(r => setIntents(r.data));
  }, []);

  return (
    <div style={{ padding: 16 }}>
      <h3>Live Intent Stream</h3>
      <table width="100%" cellPadding="6" style={{ fontSize: 13 }}>
        <thead>
          <tr>
            <th>Time</th><th>Domain</th><th>Action</th><th>Decision</th><th>Replay</th>
          </tr>
        </thead>
        <tbody>
          {intents.map((i, k) => (
            <tr key={k}>
              <td>{i.timestamp?.slice(11,19)}</td>
              <td>{i.domain}</td>
              <td>{i.action}</td>
              <td>{i.decision}</td>
              <td>
                <button onClick={() => setOpen(i.intent_hash)}>
                  {i.intent_hash.slice(0,10)}…
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <ReplayDrawer hash={open} onClose={() => setOpen(null)} />
    </div>
  );
}
