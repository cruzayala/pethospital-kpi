-- Migration 030: Add configuration and reports tables
-- Date: 2025-11-20
-- Description: Add system configuration, company logos, and report management tables

-- System configuration table
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255),
    company_address TEXT,
    company_phone VARCHAR(50),
    company_email VARCHAR(255),
    timezone VARCHAR(50) DEFAULT 'America/Santo_Domingo',
    language VARCHAR(10) DEFAULT 'es',
    theme VARCHAR(20) DEFAULT 'light',
    reports_email VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Company logos table (supports multiple logos per center)
CREATE TABLE IF NOT EXISTS company_logos (
    id SERIAL PRIMARY KEY,
    center_id INTEGER REFERENCES centers(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    mime_type VARCHAR(50) NOT NULL,
    file_size INTEGER,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Report templates table (saved report configurations)
CREATE TABLE IF NOT EXISTS report_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    filters JSONB,
    metrics JSONB,
    format VARCHAR(10) DEFAULT 'pdf',
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Generated reports table (history of generated reports)
CREATE TABLE IF NOT EXISTS generated_reports (
    id SERIAL PRIMARY KEY,
    template_id INTEGER REFERENCES report_templates(id) ON DELETE SET NULL,
    report_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_size INTEGER,
    format VARCHAR(10),
    filters_used JSONB,
    generated_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    generated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP  -- Optional: auto-delete old reports
);

-- Insert default system configuration
INSERT INTO system_config (company_name, company_address, company_phone, company_email, timezone, language, theme)
VALUES ('PetHospital KPI', '', '', 'info@pethospital-kpi.com', 'America/Santo_Domingo', 'es', 'light')
ON CONFLICT DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_company_logos_center ON company_logos(center_id);
CREATE INDEX IF NOT EXISTS idx_company_logos_active ON company_logos(is_active) WHERE is_active = TRUE;
-- Unique partial index to ensure only one active logo per center
CREATE UNIQUE INDEX IF NOT EXISTS idx_company_logos_center_active ON company_logos(center_id) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_report_templates_created_by ON report_templates(created_by);
CREATE INDEX IF NOT EXISTS idx_generated_reports_generated_by ON generated_reports(generated_by);
CREATE INDEX IF NOT EXISTS idx_generated_reports_generated_at ON generated_reports(generated_at);

-- Add comments for documentation
COMMENT ON TABLE system_config IS 'Global system configuration settings';
COMMENT ON TABLE company_logos IS 'Company logos uploaded by centers (one active per center)';
COMMENT ON TABLE report_templates IS 'Saved report configurations for quick generation';
COMMENT ON TABLE generated_reports IS 'History of generated reports with metadata';
