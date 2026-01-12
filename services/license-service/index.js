const express = require('express');
const jwt = require('jsonwebtoken');
const { Pool } = require('pg');
const crypto = require('crypto');

const app = express();
app.use(express.json());

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
});

const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret-change-in-production';

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'license-service' });
});

// Issue new license
app.post('/api/licenses/issue', async (req, res) => {
  const { 
    tenant_id, 
    module_id, 
    quota_tokens = 1000000,
    quota_calls = 10000,
    duration_days = 30 
  } = req.body;
  
  if (!tenant_id || !module_id) {
    return res.status(400).json({ error: 'tenant_id and module_id are required' });
  }
  
  const client = await pool.connect();
  
  try {
    await client.query('BEGIN');
    
    const moduleCheck = await client.query(
      'SELECT module_id FROM modules WHERE module_id = $1',
      [module_id]
    );
    
    if (moduleCheck.rows.length === 0) {
      await client.query('ROLLBACK');
      return res.status(404).json({ error: 'Module not found' });
    }
    
    const license_id = `lic_${Date.now()}_${crypto.randomBytes(8).toString('hex')}`;
    const expiry = new Date(Date.now() + duration_days * 24 * 60 * 60 * 1000);
    
    await client.query(
      `INSERT INTO licenses 
       (license_id, tenant_id, module_id, version_range, quota_tokens, quota_calls, expiry, status)
       VALUES ($1, $2, $3, $4, $5, $6, $7, 'active')`,
      [license_id, tenant_id, module_id, '^1.0.0', quota_tokens, quota_calls, expiry]
    );
    
    const token = jwt.sign({
      license_id,
      tenant_id,
      module_id,
      limits: { max_tokens: quota_tokens, max_calls: quota_calls },
      expiry: expiry.getTime(),
      issued_at: Date.now()
    }, JWT_SECRET, { expiresIn: `${duration_days}d` });
    
    await client.query('COMMIT');
    
    console.log(`✅ License issued: ${license_id}`);
    
    res.status(201).json({ 
      success: true,
      license_id, 
      token,
      expiry: expiry.toISOString()
    });
    
  } catch (error) {
    await client.query('ROLLBACK');
    console.error('❌ License error:', error);
    res.status(500).json({ error: 'Failed to issue license', details: error.message });
  } finally {
    client.release();
  }
});

// Validate license
app.post('/api/licenses/validate', async (req, res) => {
  const { token } = req.body;
  
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    const result = await pool.query(
      'SELECT * FROM licenses WHERE license_id = $1',
      [decoded.license_id]
    );
    
    if (result.rows.length === 0) {
      return res.status(401).json({ valid: false, reason: 'License not found' });
    }
    
    const license = result.rows[0];
    
    if (license.status !== 'active') {
      return res.status(401).json({ valid: false, reason: `License ${license.status}` });
    }
    
    res.json({ valid: true, license_id: license.license_id });
    
  } catch (error) {
    console.error('❌ Validation error:', error);
    res.status(401).json({ valid: false, reason: 'Invalid token' });
  }
});

// Get license info
app.get('/api/licenses/:license_id', async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT * FROM licenses WHERE license_id = $1',
      [req.params.license_id]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'License not found' });
    }
    
    res.json(result.rows[0]);
    
  } catch (error) {
    res.status(500).json({ error: 'Failed to get license' });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`🔐 License Service running on port ${PORT}`);
});
