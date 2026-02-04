export interface StatusResponse {
  status: string;
  version: string;
}

export interface HealthResponse {
  status: string;
}

export interface AuthToken {
  token: string;
  scopes: string[];
  tenant_id?: string | null;
}

export interface Tenant {
  tenant_id: string;
  name: string;
  region?: string | null;
}

export interface QuorumRules {
  rules: Record<string, any>;
}

export interface QuorumValidateResponse {
  required: number;
  approved: number;
  approvers: string[];
  roles: string[];
  intent_hash: string;
  tenant_id?: string | null;
  action: string;
  rule_id: string;
}

export interface EvidenceExportResponse {
  bundle_id: string;
  bundle_path: string;
  manifest_hash: string;
  verified: boolean;
  warnings: string[];
}

export interface ApprovalRecord {
  approval_id?: string | null;
  approver_id?: string | null;
  role?: string | null;
  region?: string | null;
  intent_hash?: string | null;
  issued_at?: number | null;
  expires_at?: number | null;
  rule_id?: string | null;
  tenant_id?: string | null;
  action?: string | null;
  timestamp?: string | null;
}

export interface AuditEvent {
  timestamp: string;
  event_type: string;
  method: string;
  path: string;
  status_code: number;
  decision: string;
  latency_ms: number;
  actor_id?: string | null;
  tenant_id?: string | null;
  role?: string | null;
  request_hash?: string | null;
  quorum?: Record<string, any> | null;
  error?: string | null;
  client_ip?: string | null;
}
