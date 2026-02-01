const express = require('express');
const { Pool } = require('pg');
const crypto = require('crypto');

const app = express();
app.use(express.json());

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
});

const STRIPE_SECRET_KEY = process.env.STRIPE_SECRET_KEY;

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'billing-service' });
});

// =========================================
// CREATE STRIPE PRODUCT FOR MODULE
// =========================================
app.post('/api/billing/products/create', async (req, res) => {
  const { module_id, publisher_id, name } = req.body;
  
  if (!STRIPE_SECRET_KEY) {
    return res.status(501).json({ 
      error: 'Stripe not configured',
      message: 'Set STRIPE_SECRET_KEY environment variable'
    });
  }
  
  try {
    // Create Stripe product
    const productResponse = await fetch('https://api.stripe.com/v1/products', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${STRIPE_SECRET_KEY}`,
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        name: name || module_id,
        'metadata[module_id]': module_id,
        'metadata[publisher_id]': publisher_id
      })
    });
    
    const product = await productResponse.json();
    
    if (product.error) {
      return res.status(400).json({ error: product.error });
    }
    
    // Create metered price (per 1K tokens)
    const priceResponse = await fetch('https://api.stripe.com/v1/prices', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${STRIPE_SECRET_KEY}`,
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        product: product.id,
        currency: 'usd',
        'recurring[interval]': 'month',
        'recurring[usage_type]': 'metered',
        billing_scheme: 'tiered',
        tiers_mode: 'graduated',
        'tiers[0][up_to]': '100000',
        'tiers[0][unit_amount_decimal]': '1.0',
        'tiers[1][up_to]': '1000000',
        'tiers[1][unit_amount_decimal]': '0.8',
        'tiers[2][up_to]': 'inf',
        'tiers[2][unit_amount_decimal]': '0.5'
      })
    });
    
    const price = await priceResponse.json();
    
    if (price.error) {
      return res.status(400).json({ error: price.error });
    }
    
    console.log(`✅ Stripe product created: ${product.id} for module ${module_id}`);
    
    res.json({ 
      success: true,
      product, 
      price 
    });
    
  } catch (error) {
    console.error('❌ Product creation error:', error);
    res.status(500).json({ error: 'Failed to create product', details: error.message });
  }
});

// =========================================
// REPORT USAGE TO STRIPE
// =========================================
app.post('/api/billing/usage/report', async (req, res) => {
  const { subscription_item_id, usage_event } = req.body;
  
  if (!STRIPE_SECRET_KEY) {
    return res.status(501).json({ 
      error: 'Stripe not configured'
    });
  }
  
  try {
    const quantity = Math.ceil(usage_event.total_tokens / 1000);
    const timestamp = Math.floor(usage_event.timestamp / 1000);
    
    const response = await fetch(
      `https://api.stripe.com/v1/subscription_items/${subscription_item_id}/usage_records`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${STRIPE_SECRET_KEY}`,
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
          quantity: quantity.toString(),
          timestamp: timestamp.toString(),
          action: 'increment'
        })
      }
    );
    
    const result = await response.json();
    
    if (result.error) {
      return res.status(400).json({ error: result.error });
    }
    
    console.log(`💰 Usage reported to Stripe: ${quantity}K tokens`);
    
    res.json({ 
      success: true,
      usage_record: result 
    });
    
  } catch (error) {
    console.error('❌ Usage reporting error:', error);
    res.status(500).json({ error: 'Failed to report usage', details: error.message });
  }
});

// =========================================
// CALCULATE ROYALTIES
// =========================================
app.post('/api/billing/royalties/calculate', async (req, res) => {
  const { publisher_id, period_start, period_end } = req.body;
  
  try {
    // Get all usage for publisher's modules in period
    const usageResult = await pool.query(
      `SELECT 
        COUNT(*) as total_requests,
        SUM(ue.total_tokens) as total_tokens,
        SUM(ue.cost_calculated) as gross_revenue,
        COUNT(DISTINCT ue.tenant_id) as unique_tenants
       FROM usage_events ue
       JOIN modules m ON ue.module_id = m.module_id
       WHERE m.publisher_id = $1
         AND ue.created_at BETWEEN $2 AND $3`,
      [publisher_id, period_start, period_end]
    );
    
    const usage = usageResult.rows[0];
    const gross_revenue = parseFloat(usage.gross_revenue || 0);
    const platform_fee_percent = 15.0; // 15% platform fee
    const platform_fee = gross_revenue * (platform_fee_percent / 100);
    const net_payout = gross_revenue - platform_fee;
    
    // Create royalty statement
    const statement_id = `stmt_${Date.now()}_${crypto.randomBytes(6).toString('hex')}`;
    
    await pool.query(
      `INSERT INTO royalty_statements 
       (statement_id, period_start, period_end, publisher_id, 
        total_tokens, total_calls, total_requests, unique_tenants,
        gross_revenue, platform_fee, platform_fee_percent, net_payout, status)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, 'pending')`,
      [
        statement_id, period_start, period_end, publisher_id,
        usage.total_tokens, usage.total_requests, usage.total_requests, usage.unique_tenants,
        gross_revenue, platform_fee, platform_fee_percent, net_payout
      ]
    );
    
    console.log(`📊 Royalty statement created: ${statement_id} for ${publisher_id}`);
    
    res.json({
      success: true,
      statement_id,
      period: { start: period_start, end: period_end },
      publisher_id,
      metrics: {
        total_requests: parseInt(usage.total_requests),
        total_tokens: parseInt(usage.total_tokens || 0),
        unique_tenants: parseInt(usage.unique_tenants)
      },
      financial: {
        gross_revenue,
        platform_fee,
        platform_fee_percent,
        net_payout
      }
    });
    
  } catch (error) {
    console.error('❌ Royalty calculation error:', error);
    res.status(500).json({ error: 'Failed to calculate royalties', details: error.message });
  }
});

// =========================================
// GET ROYALTY STATEMENTS
// =========================================
app.get('/api/billing/royalties/:publisher_id', async (req, res) => {
  const { publisher_id } = req.params;
  const { status } = req.query;
  
  try {
    let query = `
      SELECT * FROM royalty_statements 
      WHERE publisher_id = $1
    `;
    const params = [publisher_id];
    
    if (status) {
      query += ` AND status = $2`;
      params.push(status);
    }
    
    query += ` ORDER BY period_start DESC`;
    
    const result = await pool.query(query, params);
    
    res.json({
      count: result.rows.length,
      statements: result.rows
    });
    
  } catch (error) {
    console.error('❌ Get royalties error:', error);
    res.status(500).json({ error: 'Failed to retrieve royalties', details: error.message });
  }
});

// =========================================
// STRIPE WEBHOOK HANDLER
// =========================================
app.post('/api/billing/webhook', async (req, res) => {
  const event = req.body;
  
  try {
    console.log(`📨 Stripe webhook received: ${event.type}`);
    
    switch (event.type) {
      case 'invoice.payment_succeeded':
        const invoice = event.data.object;
        console.log(`✅ Payment succeeded: ${invoice.id}`);
        // Update royalty statement status
        break;
        
      case 'invoice.payment_failed':
        const failedInvoice = event.data.object;
        console.log(`❌ Payment failed: ${failedInvoice.id}`);
        break;
        
      case 'customer.subscription.created':
        const subscription = event.data.object;
        console.log(`📝 Subscription created: ${subscription.id}`);
        break;
        
      case 'customer.subscription.deleted':
        const deletedSub = event.data.object;
        // Deactivate associated licenses
        await pool.query(
          `UPDATE licenses 
           SET status = 'cancelled', updated_at = NOW()
           WHERE stripe_subscription_id = $1`,
          [deletedSub.id]
        );
        console.log(`🚫 Subscription cancelled: ${deletedSub.id}`);
        break;
    }
    
    res.json({ received: true });
    
  } catch (error) {
    console.error('❌ Webhook error:', error);
    res.status(500).json({ error: 'Webhook processing failed', details: error.message });
  }
});

const PORT = process.env.PORT || 3003;
app.listen(PORT, () => {
  console.log(`💰 Billing Service running on port ${PORT}`);
});
