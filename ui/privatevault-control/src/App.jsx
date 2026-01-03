import StatusBar from "./components/StatusBar";
import IntentTable from "./components/IntentTable";
import ShadowImpactPanel from "./components/ShadowImpactPanel";

export default function App() {
  return (
    <div style={{
      background: "#0f0f0f",
      minHeight: "100vh",
      color: "#ddd",
      fontFamily: "system-ui, sans-serif"
    }}>
      <StatusBar />

      <div style={{ display: "flex" }}>
        <div style={{ flex: 1 }}>
          <IntentTable />
        </div>

        <ShadowImpactPanel />
      </div>
    </div>
  );
}
