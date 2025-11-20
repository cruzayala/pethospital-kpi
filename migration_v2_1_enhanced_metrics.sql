-- ============================================================================
-- Migration Script: Enhanced Metrics v2.1
-- Description: Adds intelligent metrics tables for performance, modules,
--              system usage, and payment methods
-- Date: 2025-11-19
-- ============================================================================

-- Create performance_metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    center_id INTEGER NOT NULL REFERENCES centers(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    avg_order_processing_time INTEGER,  -- Average time from order to result (in minutes)
    peak_hour INTEGER,                   -- Hour of day with most activity (0-23)
    peak_hour_orders INTEGER,            -- Number of orders in peak hour
    completion_rate INTEGER,             -- Percentage of orders completed (0-100)
    same_day_completion INTEGER,         -- Number of orders completed same day
    morning_orders INTEGER DEFAULT 0,    -- 6am-12pm
    afternoon_orders INTEGER DEFAULT 0,  -- 12pm-6pm
    evening_orders INTEGER DEFAULT 0,    -- 6pm-12am
    night_orders INTEGER DEFAULT 0,      -- 12am-6am
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for performance_metrics
CREATE INDEX IF NOT EXISTS idx_performance_metrics_center_date
    ON performance_metrics(center_id, date);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_date
    ON performance_metrics(date);

-- Create module_metrics table
CREATE TABLE IF NOT EXISTS module_metrics (
    id SERIAL PRIMARY KEY,
    center_id INTEGER NOT NULL REFERENCES centers(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    module_name VARCHAR(100) NOT NULL,   -- laboratorio, consultas, farmacia, etc.
    operations_count INTEGER DEFAULT 0,  -- Total operations in this module
    active_users INTEGER DEFAULT 0,      -- Number of different users who used the module
    total_revenue INTEGER,               -- Total revenue generated (in cents)
    avg_transaction INTEGER,             -- Average transaction value (in cents)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for module_metrics
CREATE INDEX IF NOT EXISTS idx_module_metrics_center_date
    ON module_metrics(center_id, date);
CREATE INDEX IF NOT EXISTS idx_module_metrics_date
    ON module_metrics(date);
CREATE INDEX IF NOT EXISTS idx_module_metrics_module_name
    ON module_metrics(module_name);

-- Create system_usage_metrics table
CREATE TABLE IF NOT EXISTS system_usage_metrics (
    id SERIAL PRIMARY KEY,
    center_id INTEGER NOT NULL REFERENCES centers(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_active_users INTEGER DEFAULT 0,      -- Total users active on this day
    peak_concurrent_users INTEGER DEFAULT 0,   -- Maximum simultaneous users
    avg_session_duration INTEGER,              -- Average session in minutes
    web_access_count INTEGER DEFAULT 0,        -- Accesses via web
    mobile_access_count INTEGER DEFAULT 0,     -- Accesses via mobile
    desktop_access_count INTEGER DEFAULT 0,    -- Accesses via desktop
    total_workstations INTEGER DEFAULT 0,      -- Number of workstations
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for system_usage_metrics
CREATE INDEX IF NOT EXISTS idx_system_usage_metrics_center_date
    ON system_usage_metrics(center_id, date);
CREATE INDEX IF NOT EXISTS idx_system_usage_metrics_date
    ON system_usage_metrics(date);

-- Create payment_method_metrics table
CREATE TABLE IF NOT EXISTS payment_method_metrics (
    id SERIAL PRIMARY KEY,
    center_id INTEGER NOT NULL REFERENCES centers(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    payment_method VARCHAR(50) NOT NULL,  -- efectivo, tarjeta, transferencia, seguro
    transaction_count INTEGER DEFAULT 0,   -- Number of transactions
    total_amount INTEGER,                  -- Total amount (in cents)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for payment_method_metrics
CREATE INDEX IF NOT EXISTS idx_payment_method_metrics_center_date
    ON payment_method_metrics(center_id, date);
CREATE INDEX IF NOT EXISTS idx_payment_method_metrics_date
    ON payment_method_metrics(date);

-- ============================================================================
-- Verification queries
-- ============================================================================

-- Verify all tables were created
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN (
        'performance_metrics',
        'module_metrics',
        'system_usage_metrics',
        'payment_method_metrics'
    )
ORDER BY tablename;

-- Show table structures
\d performance_metrics;
\d module_metrics;
\d system_usage_metrics;
\d payment_method_metrics;

-- ============================================================================
-- Rollback script (if needed)
-- ============================================================================
-- Uncomment to rollback this migration:

-- DROP TABLE IF EXISTS payment_method_metrics CASCADE;
-- DROP TABLE IF EXISTS system_usage_metrics CASCADE;
-- DROP TABLE IF EXISTS module_metrics CASCADE;
-- DROP TABLE IF EXISTS performance_metrics CASCADE;
