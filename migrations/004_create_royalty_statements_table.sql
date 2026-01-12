-- Royalty Statements Table
CREATE TABLE IF NOT EXISTS royalty_statements (
    statement_id VARCHAR(255) PRIMARY KEY,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    publisher_id VARCHAR(255) NOT NULL,
    
    -- Usage Stats
    total_tokens BIGINT NOT NULL,
    total_calls INTEGER NOT NULL,
    total_requests INTEGER NOT NULL,
    
    -- Financial
    total_due DECIMAL(10,2) NOT NULL,
    platform_fee DECIMAL(10,2) NOT NULL,
    net_payout DECIMAL(10,2) NOT NULL,
    
    -- Status
    status VARCHAR(20) CHECK (status IN ('pending', 'processing', 'paid', 'failed')) DEFAULT 'pending',
    paid_at TIMESTAMP,
    
    -- Stripe Payout
    stripe_payout_id VARCHAR(255),
    stripe_transfer_id VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(publisher_id, period_start, period_end)
);
-- Postgres indexes
CREATE INDEX IF NOT EXISTS idx_royalty_publisher_period ON royalty_statements(publisher_id, period_start);
CREATE INDEX IF NOT EXISTS idx_royalty_status ON royalty_statements(status);
