const express = require('express');
const jwt = require('jsonwebtoken');
const { Pool } = require('pg');

const app = express();
app.use(express.json());

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const JWT_SECRET = process.env.JWT_SECRET || 'dev_secret_change_me';

function id(prefix) {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
}

app.post('/api/licenses/issue', async (req, res) => {
  const { tenant_id, module_id, quota_tokens, quota_calls, duration_days } = req.body;
  try {
    if (!tenant_id || !module_id) return res.status(400).json({ error: 'tenant_id and module_id required' });

    const license_id = id('lic');
    const days = duration_days || 30;
    const expiry = new Date(Date.now() + days * 24 * 60 * 60 * 1000);

    await pool.query(
      `INSERT INTO licenses
       (license_id, tenant_id, module_id, version_range, quota_tokens, quota_calls, expiry, status)
       VALUES ($1,$2,$3,$4,$5,$6,$7,'active')`,
      [license_id, tenant_id, module_id, '^1.0.0', quota_tokens || null, quota_calls || null, expiry]
    );

    const token = jwt.sign(
      {
        license_id,
        tenant_id,
        module_id,
        limits: { max_tokens: quota_tokens || null, max_calls: quota_calls || null },
        expiry: expiry.getTime(),
        issued_at: Date.now()
      },
      JWT_SECRET,
      { expiresIn: `${days}d` }
    );

    res.json({ license_id, token, expiry: expiry.toISOString() });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Failed to issue license' });
  }
});

app.post('/api/licenses/validate', async (req, res) => {
  const { token, module_id } = req.body;
  try {
    const decoded = jwt.verify(token, JWT_SECRET);

    const r = await pool.query(
      `SELECT * FROM licenses WHERE license_id=$1 AND status='active'`,
      [decoded.license_id]
    );
    if (!r.rows.length) return res.status(401).json({ valid: false, reason: 'License not found/inactive' });

    const lic = r.rows[0];

    if (new Date(lic.expiry) < new Date()) return res.status(401).json({ valid: false, reason: 'License expired' });
    if (lic.module_id !== module_id) return res.status(401).json({ valid: false, reason: 'Module mismatch' });

    if (lic.quota_tokens && lic.tokens_used >= lic.quota_tokens) {
      return res.status(429).json({ valid: false, reason: 'Token quota exhausted' });
    }

    const quota_remaining = lic.quota_tokens ? (lic.quota_tokens - lic.tokens_used) : null;
    res.json({ valid: true, license_id: lic.license_id, module_id: lic.module_id, quota_remaining });
  } catch (e) {
    if (e.name === 'JsonWebTokenError') return res.status(401).json({ valid: false, reason: 'Invalid token' });
    console.error(e);
    res.status(500).json({ error: 'Validation failed' });
  }
});

app.post('/api/licenses/usage', async (req, res) => {
  const { license_id, tokens_used, calls_made } = req.body;
  try {
    await pool.query(
      `UPDATE licenses
       SET tokens_used=tokens_used+$2,
           calls_used=calls_used+$3,
           updated_at=NOW()
       WHERE license_id=$1`,
      [license_id, tokens_used || 0, calls_made || 1]
    );
    res.json({ success: true });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Failed to update usage' });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`License Service running on port ${PORT}`));
