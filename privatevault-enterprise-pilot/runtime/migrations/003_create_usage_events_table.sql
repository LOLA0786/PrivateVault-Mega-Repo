-- Usage Events Table (Append-Only Immutable Log)
CREATE TABLE IF NOT EXISTS usage_events (
    event_id VARCHAR(255) PRIMARY KEY,
    request_id VARCHAR(255) NOT NULL,
    timestamp BIGINT NOT NULL,
    
    -- Identity
    tenant_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    agent_id VARCHAR(255),
    
    -- Module Usage
    module_id VARCHAR(255) REFERENCES modules(module_id),
    module_version VARCHAR(50) NOT NULL,
    chunks_used JSONB NOT NULL,
    
    -- Token Attribution
    prompt_tokens_attributed INTEGER NOT NULL,
    response_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    
    -- Asset Usage
    assets_used JSONB,
    
    -- Billing
    cost_calculated DECIMAL(10,6) NOT NULL,
    license_id VARCHAR(255) REFERENCES licenses(license_id),
    
    -- Integrity
    signature TEXT NOT NULL,
    hash VARCHAR(64) NOT NULL,
    
    created_at TIMESTAMP DEFAULT NOW()
);
-- Prevent updates/deletes on usage_events (immutable log)
CREATE OR REPLACE RULE usage_events_no_update AS 
    ON UPDATE TO usage_events DO INSTEAD NOTHING;

CREATE OR REPLACE RULE usage_events_no_delete AS 
    ON DELETE TO usage_events DO INSTEAD NOTHING;

-- Postgres indexes
CREATE INDEX IF NOT EXISTS idx_usage_tenant_time ON usage_events(tenant_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_usage_module_time ON usage_events(module_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_usage_request ON usage_events(request_id);
CREATE INDEX IF NOT EXISTS idx_usage_license ON usage_events(license_id);
