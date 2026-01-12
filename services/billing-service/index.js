const express = require('express');
const { Pool } = require('pg');

const app = express();
app.use(express.json());

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

// NOTE: In production use Stripe SDK + webhook signature verification.
// Here is a minimal stub service.
app.get('/health', (req, res) => res.json({ ok: true }));

app.post('/api/billing/webhook', async (req, res) => {
  try {
    const event = req.body;

    if (event?.type === 'customer.subscription.deleted') {
      const subscription = event.data.object;
      await pool.query(
        `UPDATE licenses SET status='cancelled' WHERE stripe_subscription_id=$1`,
        [subscription.id]
      );
    }

    res.json({ received: true });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Webhook failed' });
  }
});

const PORT = process.env.PORT || 3003;
app.listen(PORT, () => console.log(`Billing Service running on port ${PORT}`));
