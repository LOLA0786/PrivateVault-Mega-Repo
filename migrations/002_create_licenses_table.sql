-- Licenses Table
CREATE TABLE IF NOT EXISTS licenses (
    license_id VARCHAR(255) PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    module_id VARCHAR(255) REFERENCES modules(module_id) ON DELETE CASCADE,
    version_range VARCHAR(50) NOT NULL,
    
    -- Quotas
    quota_tokens BIGINT,
    quota_calls INTEGER,
    quota_users INTEGER,
    
    -- Usage Tracking
    tokens_used BIGINT DEFAULT 0,
    calls_used INTEGER DEFAULT 0,
    users_active INTEGER DEFAULT 0,
    
    -- Validity
    issued_at TIMESTAMP DEFAULT NOW(),
    expiry TIMESTAMP NOT NULL,
    status VARCHAR(20) CHECK (status IN ('active', 'suspended', 'expired', 'cancelled')) DEFAULT 'active',
    
    -- Policy Claims
    allowed_agents JSONB,
    restricted_prompts JSONB,
    
    -- Billing
    stripe_subscription_id VARCHAR(255),
    stripe_subscription_item_id VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
-- Postgres indexes
CREATE INDEX IF NOT EXISTS idx_licenses_tenant ON licenses(tenant_id);
CREATE INDEX IF NOT EXISTS idx_licenses_module ON licenses(module_id);
CREATE INDEX IF NOT EXISTS idx_licenses_expiry ON licenses(expiry);
CREATE INDEX IF NOT EXISTS idx_licenses_status ON licenses(status);
