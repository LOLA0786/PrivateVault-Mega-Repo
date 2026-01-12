-- Module Registry Table
CREATE TABLE IF NOT EXISTS modules (
    module_id VARCHAR(255) PRIMARY KEY,
    publisher_id VARCHAR(255) NOT NULL,
    current_version VARCHAR(50) NOT NULL,
    hash VARCHAR(64) NOT NULL,
    storage_uri TEXT NOT NULL,
    encryption_key_id VARCHAR(255),
    pricing_plan_id VARCHAR(255),
    
    -- License Configuration
    license_type VARCHAR(50) CHECK (license_type IN ('subscription', 'pay-per-use', 'enterprise', 'trial')),
    base_price DECIMAL(10,2),
    per_token_rate DECIMAL(10,6),
    per_call_rate DECIMAL(10,4),
    
    -- Policy
    allowed_industries JSONB,
    allowed_geos JSONB,
    restricted_users JSONB,
    
    -- Attribution
    author VARCHAR(255),
    org VARCHAR(255),
    identity_key TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
-- Module Chunks Table (for tracking)
CREATE TABLE IF NOT EXISTS module_chunks (
    id BIGSERIAL PRIMARY KEY,
    module_id VARCHAR(255) REFERENCES modules(module_id) ON DELETE CASCADE,
    chunk_id VARCHAR(255) NOT NULL,
    chunk_hash VARCHAR(64) NOT NULL,
    token_count INTEGER NOT NULL,
    content_preview TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(module_id, chunk_id)
);
-- Postgres indexes
CREATE INDEX IF NOT EXISTS idx_modules_publisher ON modules(publisher_id);
CREATE INDEX IF NOT EXISTS idx_modules_version ON modules(current_version);
CREATE INDEX IF NOT EXISTS idx_module_chunk ON module_chunks(module_id, chunk_id);
