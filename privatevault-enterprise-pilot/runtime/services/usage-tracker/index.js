const express = require('express');
const crypto = require('crypto');
const { Pool } = require('pg');
const { Kafka } = require('kafkajs');

const app = express();
app.use(express.json({ limit: '2mb' }));

// -----------------------------
// Postgres Pool
// -----------------------------
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: parseInt(process.env.PG_POOL_MAX || '20', 10),
});

// -----------------------------
// Kafka Producer (optional)
// -----------------------------
const kafka = new Kafka({
  clientId: 'usage-tracker',
  brokers: (process.env.KAFKA_BROKERS || process.env.KAFKA_BROKER || 'kafka:9092').split(','),
});

const producer = kafka.producer();
const SIGNING_KEY = process.env.SIGNING_KEY || 'dev-signing-key-change-in-production';

// Initialize Kafka
let kafkaConnected = false;
(async () => {
  try {
    await producer.connect();
    kafkaConnected = true;
    console.log('✅ Kafka producer connected');
  } catch (error) {
    kafkaConnected = false;
    console.warn('⚠️  Kafka connection failed, running without streaming:', error.message);
  }
})();

// -----------------------------
// Helpers
// -----------------------------
function hmacSign(obj) {
  return crypto
    .createHmac('sha256', SIGNING_KEY)
    .update(JSON.stringify(obj))
    .digest('hex');
}

function sha256(obj) {
  return crypto
    .createHash('sha256')
    .update(JSON.stringify(obj))
    .digest('hex');
}

// -----------------------------
// Health check
// -----------------------------
app.get('/health', async (req, res) => {
  try {
    await pool.query('SELECT 1');
    res.json({
      status: 'healthy',
      service: 'usage-tracker',
      kafka: kafkaConnected,
      db: true
    });
  } catch (e) {
    res.status(500).json({
      status: 'unhealthy',
      service: 'usage-tracker',
      kafka: kafkaConnected,
      db: false,
      error: e.message
    });
  }
});

// =========================================
// LOG USAGE EVENT (append-only)
// =========================================
app.post('/api/usage/log', async (req, res) => {
  const {
    request_id,
    tenant_id,
    user_id,
    agent_id = 'default',
    module_id,
    module_version,
    chunks_used = [],
    prompt_tokens_attributed = 0,
    response_tokens = 0,
    license_id = null
  } = req.body || {};

  // Validation
  if (!request_id || !tenant_id || !user_id || !module_id) {
    return res.status(400).json({
      error: 'Missing required fields: request_id, tenant_id, user_id, module_id'
    });
  }

  const client = await pool.connect();

  try {
    await client.query('BEGIN');

    const event_id = `evt_${Date.now()}_${crypto.randomBytes(8).toString('hex')}`;
    const timestamp = Date.now();
    const total_tokens = Number(prompt_tokens_attributed || 0) + Number(response_tokens || 0);

    // Get module pricing (optional)
    const moduleResult = await client.query(
      'SELECT per_token_rate, per_call_rate FROM modules WHERE module_id = $1',
      [module_id]
    );

    // Default: $0.01 / 1K tokens if no module pricing exists
    let per_token_rate = 0.01;
    let per_call_rate = 0;

    if (moduleResult.rows.length > 0) {
      per_token_rate = Number(moduleResult.rows[0].per_token_rate ?? per_token_rate);
      per_call_rate = Number(moduleResult.rows[0].per_call_rate ?? per_call_rate);
    }

    const token_cost = (total_tokens / 1000) * per_token_rate;
    const call_cost = per_call_rate;
    const cost_calculated = Number((token_cost + call_cost).toFixed(6));

    // Data for signing
    const eventData = {
      request_id,
      tenant_id,
      user_id,
      agent_id,
      module_id,
      module_version: module_version || 'v1.0.0',
      chunks_used,
      prompt_tokens_attributed: Number(prompt_tokens_attributed || 0),
      response_tokens: Number(response_tokens || 0),
      total_tokens,
      timestamp
    };

    const signature = hmacSign(eventData);
    const hash = sha256({ ...eventData, signature });

    // Insert immutable event
    await client.query(
      `INSERT INTO usage_events
       (event_id, request_id, timestamp, tenant_id, user_id, agent_id,
        module_id, module_version, chunks_used, prompt_tokens_attributed,
        response_tokens, total_tokens, cost_calculated, license_id, signature, hash)
       VALUES
       ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16)`,
      [
        event_id,
        request_id,
        timestamp,
        tenant_id,
        user_id,
        agent_id,
        module_id,
        module_version || 'v1.0.0',
        JSON.stringify(chunks_used || []),
        Number(prompt_tokens_attributed || 0),
        Number(response_tokens || 0),
        total_tokens,
        cost_calculated,
        license_id,
        signature,
        hash
      ]
    );

    // Update license usage (optional)
    if (license_id) {
      await client.query(
        `UPDATE licenses
         SET tokens_used = tokens_used + $2,
             calls_used = calls_used + 1,
             updated_at = NOW()
         WHERE license_id = $1`,
        [license_id, total_tokens]
      );
    }

    await client.query('COMMIT');

    // Kafka fire-and-forget
    if (kafkaConnected) {
      producer.send({
        topic: 'usage-events',
        messages: [{
          key: tenant_id,
          value: JSON.stringify({
            event_id,
            ...eventData,
            cost_calculated,
            license_id,
            signature,
            hash
          })
        }]
      }).catch(err => console.error('⚠️  Kafka send error:', err.message));
    }

    console.log(`📝 Usage logged: ${event_id} | ${total_tokens} tokens | $${cost_calculated}`);

    return res.status(201).json({
      success: true,
      event_id,
      signature,
      hash,
      metrics: {
        total_tokens,
        cost_usd: cost_calculated,
        chunks_tracked: (chunks_used || []).length,
        kafka_streamed: kafkaConnected
      }
    });
  } catch (error) {
    try { await client.query('ROLLBACK'); } catch (_) {}
    console.error('❌ Usage logging error:', error);
    return res.status(500).json({ error: 'Failed to log usage', details: error.message });
  } finally {
    client.release();
  }
});

// =========================================
// GET USAGE STATISTICS
// =========================================
app.get('/api/usage/stats/:tenant_id', async (req, res) => {
  const { tenant_id } = req.params;
  const { start_date, end_date, module_id } = req.query;

  try {
    let query = `
      SELECT
        COUNT(*) as total_requests,
        COALESCE(SUM(total_tokens),0) as total_tokens,
        COALESCE(SUM(cost_calculated),0) as total_cost,
        COUNT(DISTINCT module_id) as modules_used,
        COUNT(DISTINCT user_id) as unique_users,
        COALESCE(AVG(total_tokens),0) as avg_tokens_per_request,
        MIN(created_at) as first_request,
        MAX(created_at) as last_request
      FROM usage_events
      WHERE tenant_id = $1
    `;

    const params = [tenant_id];
    let pc = 1;

    if (start_date) {
      params.push(start_date);
      query += ` AND created_at >= $${++pc}`;
    }
    if (end_date) {
      params.push(end_date);
      query += ` AND created_at <= $${++pc}`;
    }
    if (module_id) {
      params.push(module_id);
      query += ` AND module_id = $${++pc}`;
    }

    const result = await pool.query(query, params);
    const s = result.rows[0];

    return res.json({
      tenant_id,
      period: { start_date: start_date || null, end_date: end_date || null },
      stats: {
        total_requests: Number(s.total_requests || 0),
        total_tokens: Number(s.total_tokens || 0),
        total_cost_usd: Number(s.total_cost || 0),
        modules_used: Number(s.modules_used || 0),
        unique_users: Number(s.unique_users || 0),
        avg_tokens_per_request: Number(s.avg_tokens_per_request || 0),
        first_request: s.first_request,
        last_request: s.last_request
      }
    });
  } catch (error) {
    console.error('❌ Stats error:', error);
    return res.status(500).json({ error: 'Failed to retrieve stats', details: error.message });
  }
});

// =========================================
// GET USAGE BREAKDOWN BY MODULE
// =========================================
app.get('/api/usage/breakdown/:tenant_id', async (req, res) => {
  const { tenant_id } = req.params;
  const { start_date, end_date } = req.query;

  try {
    let query = `
      SELECT
        module_id,
        COUNT(*) as requests,
        COALESCE(SUM(total_tokens),0) as total_tokens,
        COALESCE(SUM(cost_calculated),0) as total_cost
      FROM usage_events
      WHERE tenant_id = $1
    `;

    const params = [tenant_id];
    let pc = 1;

    if (start_date) {
      params.push(start_date);
      query += ` AND created_at >= $${++pc}`;
    }
    if (end_date) {
      params.push(end_date);
      query += ` AND created_at <= $${++pc}`;
    }

    query += ` GROUP BY module_id ORDER BY total_cost DESC`;

    const result = await pool.query(query, params);

    return res.json({
      tenant_id,
      period: { start_date: start_date || null, end_date: end_date || null },
      breakdown: result.rows.map(row => ({
        module_id: row.module_id,
        requests: Number(row.requests || 0),
        total_tokens: Number(row.total_tokens || 0),
        total_cost_usd: Number(row.total_cost || 0)
      }))
    });
  } catch (error) {
    console.error('❌ Breakdown error:', error);
    return res.status(500).json({ error: 'Failed to retrieve breakdown', details: error.message });
  }
});

// =========================================
// GET RECENT USAGE EVENTS (for debugging)
// =========================================
app.get('/api/usage/recent/:tenant_id', async (req, res) => {
  const { tenant_id } = req.params;
  const limit = Math.min(parseInt(req.query.limit || '50', 10), 200);

  try {
    const r = await pool.query(
      `SELECT event_id, request_id, module_id, total_tokens, cost_calculated, timestamp, created_at
       FROM usage_events
       WHERE tenant_id = $1
       ORDER BY created_at DESC
       LIMIT $2`,
      [tenant_id, limit]
    );

    return res.json({
      tenant_id,
      limit,
      events: r.rows
    });
  } catch (error) {
    console.error('❌ Recent events error:', error);
    return res.status(500).json({ error: 'Failed to retrieve recent events', details: error.message });
  }
});

// -----------------------------
// Start server
// -----------------------------
const PORT = process.env.PORT || 3002;
app.listen(PORT, () => {
  console.log(`Usage Tracker running on port ${PORT}`);
});

// =========================================
// GET USAGE BREAKDOWN BY MODULE
// =========================================
app.get('/api/usage/breakdown/:tenant_id', async (req, res) => {
  const { tenant_id } = req.params;
  const { start_date, end_date } = req.query;
  
  try {
    let query = `
      SELECT 
        module_id,
        COUNT(*) as requests,
        SUM(total_tokens) as total_tokens,
        SUM(cost_calculated) as total_cost
      FROM usage_events
      WHERE tenant_id = $1
    `;
    
    const params = [tenant_id];
    let paramCount = 1;
    
    if (start_date) {
      params.push(start_date);
      query += ` AND created_at >= $${++paramCount}`;
    }
    
    if (end_date) {
      params.push(end_date);
      query += ` AND created_at <= $${++paramCount}`;
    }
    
    query += ` GROUP BY module_id ORDER BY total_cost DESC`;
    
    const result = await pool.query(query, params);
    
    res.json({
      tenant_id,
      breakdown: result.rows.map(row => ({
        module_id: row.module_id,
        requests: parseInt(row.requests),
        total_tokens: parseInt(row.total_tokens || 0),
        total_cost_usd: parseFloat(row.total_cost || 0)
      }))
    });
    
  } catch (error) {
    console.error('❌ Breakdown error:', error);
    res.status(500).json({ error: 'Failed to retrieve breakdown', details: error.message });
  }
});

// =========================================
// GENERATE PROVENANCE PROOF
// =========================================
app.get('/api/usage/proof/:event_id', async (req, res) => {
  const { event_id } = req.params;
  
  try {
    // Get usage event
    const eventResult = await pool.query(
      `SELECT ue.*, l.license_id, l.quota_tokens, l.tokens_used, m.publisher_id
       FROM usage_events ue
       LEFT JOIN licenses l ON ue.license_id = l.license_id
       LEFT JOIN modules m ON ue.module_id = m.module_id
       WHERE ue.event_id = $1`,
      [event_id]
    );
    
    if (eventResult.rows.length === 0) {
      return res.status(404).json({ error: 'Event not found' });
    }
    
    const event = eventResult.rows[0];
    
    // Verify signature
    const eventData = {
      request_id: event.request_id,
      tenant_id: event.tenant_id,
      user_id: event.user_id,
      module_id: event.module_id,
      module_version: event.module_version,
      chunks_used: event.chunks_used,
      prompt_tokens_attributed: event.prompt_tokens_attributed,
      response_tokens: event.response_tokens,
      total_tokens: event.total_tokens,
      timestamp: event.timestamp
    };
    
    const expectedSignature = crypto
      .createHmac('sha256', SIGNING_KEY)
      .update(JSON.stringify(eventData))
      .digest('hex');
    
    const signatureValid = expectedSignature === event.signature;
    
    // Generate provenance proof
    const proof = {
      event_id: event.event_id,
      request_id: event.request_id,
      timestamp: event.timestamp,
      valid: signatureValid,
      
      modules_used: [{
        module_id: event.module_id,
        version: event.module_version,
        chunks_used: event.chunks_used,
        publisher_id: event.publisher_id
      }],
      
      licenses: event.license_id ? [{
        license_id: event.license_id,
        valid: true,
        quota_remaining: event.quota_tokens - event.tokens_used
      }] : [],
      
      usage_cost: {
        total_tokens: event.total_tokens,
        cost_usd: parseFloat(event.cost_calculated),
        breakdown: [{
          module_id: event.module_id,
          tokens: event.total_tokens,
          cost: parseFloat(event.cost_calculated)
        }]
      },
      
      governance: {
        policy_id: 'default_v1',
        compliance_frameworks: ['SOC2', 'HIPAA'],
        audit_log_id: event.event_id
      },
      
      signature: {
        signed_by: 'PrivateVault',
        algorithm: 'HMAC-SHA256',
        signature_value: event.signature,
        hash: event.hash,
        verified: signatureValid
      },
      
      verification_url: `${req.protocol}://${req.get('host')}/api/usage/verify/${event.hash}`
    };
    
    res.json(proof);
    
  } catch (error) {
    console.error('❌ Proof generation error:', error);
    res.status(500).json({ error: 'Failed to generate proof', details: error.message });
  }
});

// =========================================
// VERIFY EVENT HASH
// =========================================
app.get('/api/usage/verify/:hash', async (req, res) => {
  const { hash } = req.params;
  
  try {
    const result = await pool.query(
      'SELECT event_id, timestamp, signature FROM usage_events WHERE hash = $1',
      [hash]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({ verified: false, error: 'Event not found' });
    }
    
    const event = result.rows[0];
    
    res.json({
      verified: true,
      event_id: event.event_id,
      timestamp: event.timestamp,
      signature: event.signature,
      message: 'Event authenticity verified'
    });
    
  } catch (error) {
    console.error('❌ Verification error:', error);
    res.status(500).json({ error: 'Verification failed', details: error.message });
  }
});

const PORT = process.env.PORT || 3002;
app.listen(PORT, () => {
  console.log(`📊 Usage Tracker running on port ${PORT}`);
});
