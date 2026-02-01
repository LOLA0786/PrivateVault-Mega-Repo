# PrivateVault Mega Repo — Architecture (Source of Truth)

**Purpose:** Convert probabilistic agents into deterministic systems using enforceable policy + evidence-grade governance.

> Rule: No component exists without a contract + invariants + failure modes + evidence + owner.

---

## 0) Glossary
- **Enforcement Plane:** Envoy + OPA (WASM policy). Stateless. Low latency (<5ms).
- **Governance Plane:** Stateful authority + lineage + closure workflows. Temporal + Redis.
- **Kill-and-Promote:** Auto-suspend on risky sequences. Human acknowledgment required to re-enable.
- **Evidence Pack:** Exportable audit artifact proving what happened and who signed off.

---

## 1) Core Principles
1. **Determinism at boundary:** Every action request must be allowed/denied by a policy decision.
2. **Evidence before trust:** Every decision must create a lineage record.
3. **Authority is explicit:** Responsibility must always map to named humans/roles.
4. **Replayability:** Every decision must be replayable from stored evidence.
5. **Versioned everything:** Policy/config/workflow changes must be versioned and hash-addressed.

---

## 2) System Overview (Control Loop)
### Data Plane (Stateless)
1. Client → Envoy
2. Envoy → ext_authz → OPA (WASM)
3. Decision: allow/deny
4. Decision metadata emitted

### Governance Plane (Stateful)
- Append lineage event (hash-chained)
- Evaluate risk sequence / anomaly
- If high-risk:
  - Suspend agent
  - Open case
  - ESCALATE → ACKNOWLEDGED → CLOSED

---

## 3) Trust Boundaries
- External caller is untrusted.
- Envoy+OPA are deterministic gatekeepers.
- Governance store is append-only evidence.
- Humans are the only final authority for closure.

---

## 4) Data Model (Truth)
### 4.1 Decision Event (minimal)
Required fields:
- timestamp
- request_id
- actor_id
- agent_id
- action
- result (allow/deny)
- policy_hash
- config_hash
- prev_hash, hash

### 4.2 Closure Case
States:
- OPEN → ESCALATED → ACKNOWLEDGED → CLOSED

Roles:
- Owner
- Approver
- Auditor
- IncidentCommander

---

## 5) Failure Modes (Must be observable)
- Policy load failure (WASM missing) → default deny
- Lineage write failure → fail-closed for high-risk actions
- Temporal unavailable → queue events, deny promotions
- Authority registry unavailable → deny closure actions

---

## 6) Invariants (Must always hold true)
- Hash chain never breaks.
- No CLOSED case can be ACKNOWLEDGED without escalation.
- Promotions require Approver/Owner role.
- Evidence pack contains case + chain head hash.

---

## 7) Operability
- Metrics: decision latency, deny rates, suspension count
- Traces: request_id joins enforcement + governance
- Logs: append-only jsonl
