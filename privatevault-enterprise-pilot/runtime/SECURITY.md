# Sovereign SDK: Security & Cryptographic Attestation Protocol

This document outlines the security architecture of the **Galani Protocol**. It is designed for high-stakes environments where AI intent must be governed by deterministic laws rather than probabilistic filters.

## 🛡️ The Zero-Trust Architecture

### 1. Cryptographic Canonicalization (Pipe-Delimited)
Most systems fail because of "JSON Drift" (slight variations in spacing or floating points). The Galani Protocol uses **Immutable Pipe-Delimited Normalization**:
* **Format:** `actor|mode|gradient`
* **Signature:** `HMAC-SHA256(Key, Normal-String)`
* **Benefit:** This ensures that the Auditor and the Gateway are always looking at the exact same mathematical representation of intent.

### 2. Pre-Execution Gating (The Brake System)
Unlike traditional "logging" which happens *after* an action, our **Governed Gateway** requires a 200-OK Authorization from the **UAAL (Conscience)** *before* the neural engine receives the instruction.
* **Shadow Mode:** Log and Alert (Non-blocking).
* **Enforce Mode:** Deterministic 403 Forbidden (Hardware-level block).

### 3. WORM Audit Ledger (Immutable History)
The `audits.worm` file follows the **Write-Once-Read-Many** principle.
* Every entry is tied to a specific **Kernel Signature**.
* **Tamper Detection:** If a single byte in the log is modified (e.g., changing a "BLOCKED" entry to "ALLOWED"), the **Audit Viewer** will instantly flag the line as `⚠️ TAMPERED` due to a signature mismatch.

### 4. Key Isolation
The `SOVEREIGN_KERNEL_KEY` is never exposed to the AI model itself. It resides only in the **UAAL Conscience**, creating a physical and logical "Air-Gap" between the AI's intelligence and its authority.

## 🚀 Threat Model Defense
| Attack Vector | Defense Mechanism |
| :--- | :--- |
| **Log Injection** | Signatures are calculated on raw intent, not log strings. |
| **Replay Attack** | Timestamps and unique hashes prevent duplicate execution. |
| **Prompt Injection** | Gradient-based thresholding ignores prompt semantics and blocks based on "Action Impact." |
| **Unauthorized Key Access** | Kernel Key is managed via encrypted `.env` or Hardware Security Modules (HSM). |

---
*Created by the Sovereign SDK Team | Galani 2026*
