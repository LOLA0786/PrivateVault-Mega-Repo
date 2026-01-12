const express = require('express');
const crypto = require('crypto');
const { Pool } = require('pg');
const { Kafka } = require('kafkajs');

const app = express();
app.use(express.json());

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

const kafka = new Kafka({
  clientId: 'usage-tracker',
  brokers: [process.env.KAFKA_BROKER || 'kafka:9092']
});

const producer = kafka.producer();
const SIGNING_KEY = process.env.SIGNING_KEY || 'dev_signing_key_change_me';

(async () => {
  await producer.connect();
  console.log('Kafka producer connected');
})();

function sha256(x) {
  return crypto.createHash('sha256').update(x).digest('hex');
}

app.post('/api/usage/log', async (req, res) => {
  const {
    request_id,
    tenant_id,
    user_id,
    agent_id,
    module_id,
    module_version,
    chunks_used,
    prompt_tokens_attributed,
    response_tokens,
    license_id
  } = req.body;

  try {
    if (!request_id || !tenant_id || !user_id) {
      return res.status(400).json({ error: 'request_id, tenant_id, user_id required' });
    }

    const event_id = `evt_${Date.now()}_${crypto.randomBytes(8).toString('hex')}`;
    const timestamp = Date.now();
    const pt = prompt_tokens_attributed || 0;
    const rt = response_tokens || 0;
    const total_tokens = pt + rt;

    // example rate
    const cost_calculated = (total_tokens / 1000) * 0.01;

    const eventData = {
      request_id,
      tenant_id,
      user_id,
      agent_id: agent_id || null,
      module_id: module_id || null,
      module_version: module_version || '1.0.0',
      chunks_used: chunks_used || [],
      prompt_tokens_attributed: pt,
      response_tokens: rt,
      total_tokens,
      timestamp
    };

    const signature = crypto
      .createHmac('sha256', SIGNING_KEY)
      .update(JSON.stringify(eventData))
      .digest('hex');

    const hash = sha256(JSON.stringify({ ...eventData, signature }));

    await pool.query(
      `INSERT INTO usage_events
       (event_id, request_id, timestamp, tenant_id, user_id, agent_id,
        module_id, module_version, chunks_used, prompt_tokens_attributed,
        response_tokens, total_tokens, cost_calculated, license_id, signature, hash)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16)`,
      [
        event_id, request_id, timestamp, tenant_id, user_id, eventData.agent_id,
        eventData.module_id, eventData.module_version, JSON.stringify(eventData.chunks_used),
        pt, rt, total_tokens, cost_calculated, license_id || null, signature, hash
      ]
    );

    producer.send({
      topic: "usage-events",
      messages: [{ key: tenant_id, value: JSON.stringify({ event_id, ...eventData, cost_calculated, license_id, signature, hash }) }]
    }).catch((e)=>console.error("kafka send failed", e));

    if (license_id) {
      await pool.query(
        `UPDATE licenses
         SET tokens_used=tokens_used+$2,
             calls_used=calls_used+1,
             updated_at=NOW()
         WHERE license_id=$1`,
        [license_id, total_tokens]
      );
    }

    res.json({ event_id, signature, hash, cost: cost_calculated });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Failed to log usage' });
  }
});

const PORT = process.env.PORT || 3002;
app.listen(PORT, () => console.log(`Usage Tracker running on port ${PORT}`));
