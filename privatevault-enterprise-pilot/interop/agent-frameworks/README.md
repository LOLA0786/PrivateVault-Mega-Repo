# PrivateVaultAgentInterop

**PrivateVaultAgentInterop** is a multi-framework interoperability + verification suite that proves **PrivateVault can sit underneath agent orchestration frameworks** as a control-plane layer for:

- tool execution interception
- policy allow/deny
- tamper-evident audit logging (hash-chain)
- replay-ready trace artifacts
- deterministic proof packs (VV-style)

This repo is designed to be a **framework certification harness**:
> "Does PrivateVault integrate with framework X — provably, with tests and evidence artifacts?"

---

## ✅ Framework Compatibility Matrix

| Framework | Status | What’s validated |
|----------|--------|------------------|
| LangChain | ✅ Verified | Tool interception + policy gate + trace |
| LangGraph | ✅ Verified | Tool interception + policy gate + trace |
| AutoGen | ✅ Verified | Function/tool wrapper + policy + trace |
| CrewAI | ✅ Verified | Tool wrapper compatibility + policy + trace |
| LlamaIndex | ✅ Verified | Offline retrieval logging + provenance trace |
| Haystack | ✅ Verified | Offline retrieval logging + provenance trace |
| Semantic Kernel | ✅ Verified | Native function compatibility + policy + trace |
| Google ADK (`google-adk`) | ✅ Verified | Tool wrapper compatibility + policy + trace |
| Mastra | ⚙️ Contract-ready | No PyPI package detected; adapter contract + tests prove integration pattern |

**Core claim:** PrivateVault is **framework-agnostic** because it wraps the *tool/function execution layer* (and optionally retrieval/memory layer).

---

## Quickstart

### 1) Clone
```bash
git clone https://github.com/LOLA0786/PrivateVaultAgentInterop.git
cd PrivateVaultAgentInterop
2) Create environment
bash
Copy code
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
3) Install dependencies
If you don’t have a requirements file yet, install the libraries as needed per framework.

bash
Copy code
pip install -U pytest
pip install -U langchain langchain-community langgraph pyautogen crewai llama-index haystack-ai semantic-kernel google-adk
✅ Run Verification (Tests)
Run the full test suite:

bash
Copy code
pytest -q
🧾 VV Evidence Pack (KoshaTrack-style)
This repo includes a VV suite that generates audit evidence artifacts after verification.

Run:

bash
Copy code
make verify_all
This executes:

Tests

Runs full pytest suite.

Tamper-proof Evidence Manifest

Generates a SHA256 hash-chain manifest of evidence artifacts.

Any modification of evidence files breaks the chain.

Evidence Bundle Export

Creates a .tar.gz evidence bundle.

Produces .sha256 checksum for later verification.

Evidence Output Locations
PrivateVault traces
privatevault/reports/evidence/pv_trace_<RUN_ID>.jsonl

VV Reports
reports/vv/evidence_manifest_<UTC>.txt

reports/vv/evidence_manifest_<UTC>.txt.sha256

reports/vv/verify_bundle_<UTC>.tar.gz

reports/vv/verify_bundle_<UTC>.sha256

Verify Integrity Later
Verify bundle integrity
bash
Copy code
sha256sum -c reports/vv/verify_bundle_<UTC>.sha256
Verify manifest file hash
bash
Copy code
sha256sum -c reports/vv/evidence_manifest_<UTC>.txt.sha256
Repo Structure
graphql
Copy code
privatevault/
  core/                     # PrivateVault shim: vault logging, policy, wrappers
  adapters/                 # Framework adapters (LangChain/LangGraph/etc.)
  tools/                    # Demo tools used across frameworks
  reports/evidence/          # Trace outputs (ignored in git)
scripts/                    # VV scripts (verify, hashchain, bundle export)
tests/                      # Test suite per framework
reports/vv/                 # VV artifacts (ignored in git)
Why this exists
Most “agent frameworks” solve orchestration.

PrivateVault solves trust.

This repo proves PrivateVault can be integrated as a universal control plane below orchestration to provide:

cryptographic auditability

reproducible/replayable execution

policy enforcement across tools

provenance for retrieval pipelines

License
MIT (or your preferred license)
