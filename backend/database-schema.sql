-- ============================================================================
-- AI COUNCIL DATABASE SCHEMA - ONE-SHOT SETUP
-- ============================================================================
-- Run this complete script in your Supabase SQL Editor
-- URL: https://supabase.com/dashboard/project/YOUR_PROJECT_ID/editor
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- DROP EXISTING TABLES (if recreating)
-- ============================================================================
DROP TABLE IF EXISTS provider_costs CASCADE;
DROP TABLE IF EXISTS user_api_keys CASCADE;
DROP TABLE IF EXISTS subtasks CASCADE;
DROP TABLE IF EXISTS responses CASCADE;
DROP TABLE IF EXISTS requests CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- ============================================================================
-- REQUESTS TABLE (AI Council Requests)
-- ============================================================================
CREATE TABLE requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    execution_mode VARCHAR(50) DEFAULT 'balanced',
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    estimated_cost DECIMAL(10, 4),
    actual_cost DECIMAL(10, 4)
);

CREATE INDEX idx_requests_user_id ON requests(user_id);
CREATE INDEX idx_requests_created_at ON requests(created_at DESC);

-- ============================================================================
-- RESPONSES TABLE
-- ============================================================================
CREATE TABLE responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID REFERENCES requests(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    confidence_score DECIMAL(3, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_responses_request_id ON responses(request_id);

-- ============================================================================
-- SUBTASKS TABLE
-- ============================================================================
CREATE TABLE subtasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID REFERENCES requests(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    assigned_agent VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    result TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_subtasks_request_id ON subtasks(request_id);

-- ============================================================================
-- USER API KEYS TABLE (Encrypted Storage)
-- ============================================================================
CREATE TABLE user_api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(100) NOT NULL,
    encrypted_key TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, provider)
);

CREATE INDEX idx_user_api_keys_user_id ON user_api_keys(user_id);

-- ============================================================================
-- PROVIDER COSTS TABLE (Cost Tracking)
-- ============================================================================
CREATE TABLE provider_costs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID REFERENCES requests(id) ON DELETE CASCADE,
    provider VARCHAR(100) NOT NULL,
    model VARCHAR(255) NOT NULL,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cost DECIMAL(10, 6) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_provider_costs_request_id ON provider_costs(request_id);

-- ============================================================================
-- TRIGGERS FOR AUTO-UPDATE TIMESTAMPS
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_api_keys_updated_at
    BEFORE UPDATE ON user_api_keys
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE subtasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE provider_costs ENABLE ROW LEVEL SECURITY;

-- Users table policies
CREATE POLICY "Users can view their own data" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update their own data" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

-- Requests table policies
CREATE POLICY "Users can view their own requests" ON requests
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can create their own requests" ON requests
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

-- Responses table policies
CREATE POLICY "Users can view responses for their requests" ON responses
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM requests
            WHERE requests.id = responses.request_id
            AND auth.uid()::text = requests.user_id::text
        )
    );

-- Subtasks table policies
CREATE POLICY "Users can view subtasks for their requests" ON subtasks
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM requests
            WHERE requests.id = subtasks.request_id
            AND auth.uid()::text = requests.user_id::text
        )
    );

-- User API keys table policies
CREATE POLICY "Users can manage their own API keys" ON user_api_keys
    FOR ALL USING (auth.uid()::text = user_id::text);

-- Provider costs table policies
CREATE POLICY "Users can view costs for their requests" ON provider_costs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM requests
            WHERE requests.id = provider_costs.request_id
            AND auth.uid()::text = requests.user_id::text
        )
    );

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- ============================================================================
-- SEED DATA (Test Admin User)
-- ============================================================================
-- Password: admin123 (CHANGE THIS IN PRODUCTION!)
INSERT INTO users (email, password_hash, name, role, is_active)
VALUES (
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQqK',
    'Admin User',
    'admin',
    true
)
ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- VERIFICATION
-- ============================================================================
SELECT 'Database setup completed successfully!' as message;
SELECT 'Total tables created: ' || COUNT(*) as tables_count 
FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
