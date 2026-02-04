import crypto from 'crypto';

export function createApproval({
  approverId,
  role,
  region,
  intentHash,
  keyId,
  secret,
  issuedAt,
  expiresAt,
  approvalId,
}) {
  const issued = issuedAt || Math.floor(Date.now() / 1000);
  const approval = {
    approval_id: approvalId || null,
    approver_id: approverId,
    role,
    region,
    intent_hash: intentHash,
    issued_at: issued,
    expires_at: expiresAt || issued + 3600,
    key_id: keyId,
  };
  const signature = crypto.createHmac('sha256', secret).update(intentHash).digest('hex');
  approval.signature = signature;
  return approval;
}
