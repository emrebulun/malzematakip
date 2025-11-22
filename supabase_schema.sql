-- ============================================
-- Construction Material Tracking System
-- Supabase (PostgreSQL) Schema
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- ENUMS (Type Definitions)
-- ============================================

-- Concrete Class Enum
CREATE TYPE concrete_class_enum AS ENUM (
    'C16', 'C20', 'C25', 'C30', 'C35', 'C40', 'GRO', 'ŞAP'
);

-- Delivery Method Enum
CREATE TYPE delivery_method_enum AS ENUM (
    'POMPALI', 'MİKSERLİ'
);

-- Mesh Type Enum
CREATE TYPE mesh_type_enum AS ENUM (
    'Q', 'R', 'TR'
);

-- ============================================
-- TABLE 1: CONCRETE LOGS (Beton)
-- ============================================

CREATE TABLE concrete_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    supplier TEXT NOT NULL,
    waybill_no TEXT NOT NULL,
    concrete_class concrete_class_enum NOT NULL,
    delivery_method delivery_method_enum NOT NULL,
    quantity_m3 FLOAT NOT NULL CHECK (quantity_m3 > 0),
    location_block TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint to prevent duplicate waybills
    CONSTRAINT unique_concrete_waybill UNIQUE(waybill_no, supplier)
);

-- Indexes for performance
CREATE INDEX idx_concrete_date ON concrete_logs(date DESC);
CREATE INDEX idx_concrete_supplier ON concrete_logs(supplier);
CREATE INDEX idx_concrete_location ON concrete_logs(location_block);
CREATE INDEX idx_concrete_created ON concrete_logs(created_at DESC);

-- ============================================
-- TABLE 2: REBAR LOGS (Demir)
-- ============================================

CREATE TABLE rebar_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    supplier TEXT NOT NULL,
    waybill_no TEXT NOT NULL,
    project_stage TEXT,  -- e.g., "3.ETAP"
    manufacturer TEXT,   -- Actual producer (e.g., Kardemir)
    
    -- Diameter-specific weights (kg)
    q8_kg FLOAT DEFAULT 0 CHECK (q8_kg >= 0),
    q10_kg FLOAT DEFAULT 0 CHECK (q10_kg >= 0),
    q12_kg FLOAT DEFAULT 0 CHECK (q12_kg >= 0),
    q14_kg FLOAT DEFAULT 0 CHECK (q14_kg >= 0),
    q16_kg FLOAT DEFAULT 0 CHECK (q16_kg >= 0),
    q18_kg FLOAT DEFAULT 0 CHECK (q18_kg >= 0),
    q20_kg FLOAT DEFAULT 0 CHECK (q20_kg >= 0),
    q22_kg FLOAT DEFAULT 0 CHECK (q22_kg >= 0),
    q25_kg FLOAT DEFAULT 0 CHECK (q25_kg >= 0),
    q28_kg FLOAT DEFAULT 0 CHECK (q28_kg >= 0),
    q32_kg FLOAT DEFAULT 0 CHECK (q32_kg >= 0),
    
    -- Total weight (auto-calculated or provided)
    total_weight_kg FLOAT NOT NULL CHECK (total_weight_kg >= 0),
    
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint
    CONSTRAINT unique_rebar_waybill UNIQUE(waybill_no, supplier)
);

-- Indexes
CREATE INDEX idx_rebar_date ON rebar_logs(date DESC);
CREATE INDEX idx_rebar_supplier ON rebar_logs(supplier);
CREATE INDEX idx_rebar_stage ON rebar_logs(project_stage);
CREATE INDEX idx_rebar_created ON rebar_logs(created_at DESC);

-- ============================================
-- TABLE 3: MESH LOGS (Çelik Hasır)
-- ============================================

CREATE TABLE mesh_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    supplier TEXT NOT NULL,
    waybill_no TEXT NOT NULL,
    mesh_type mesh_type_enum NOT NULL,
    dimensions TEXT,  -- e.g., "215x500"
    piece_count INTEGER NOT NULL CHECK (piece_count > 0),
    weight_kg FLOAT NOT NULL CHECK (weight_kg > 0),
    usage_location TEXT,  -- Where it will be used
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint
    CONSTRAINT unique_mesh_waybill UNIQUE(waybill_no, supplier)
);

-- Indexes
CREATE INDEX idx_mesh_date ON mesh_logs(date DESC);
CREATE INDEX idx_mesh_supplier ON mesh_logs(supplier);
CREATE INDEX idx_mesh_type ON mesh_logs(mesh_type);
CREATE INDEX idx_mesh_created ON mesh_logs(created_at DESC);

-- ============================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to all tables
CREATE TRIGGER update_concrete_updated_at 
    BEFORE UPDATE ON concrete_logs
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rebar_updated_at 
    BEFORE UPDATE ON rebar_logs
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mesh_updated_at 
    BEFORE UPDATE ON mesh_logs
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS FOR ANALYTICS
-- ============================================

-- Concrete summary by supplier
CREATE VIEW v_concrete_by_supplier AS
SELECT 
    supplier,
    concrete_class,
    COUNT(*) as delivery_count,
    SUM(quantity_m3) as total_quantity_m3,
    MIN(date) as first_delivery,
    MAX(date) as last_delivery
FROM concrete_logs
GROUP BY supplier, concrete_class
ORDER BY supplier, concrete_class;

-- Concrete summary by location
CREATE VIEW v_concrete_by_location AS
SELECT 
    location_block,
    concrete_class,
    COUNT(*) as delivery_count,
    SUM(quantity_m3) as total_quantity_m3
FROM concrete_logs
WHERE location_block IS NOT NULL
GROUP BY location_block, concrete_class
ORDER BY total_quantity_m3 DESC;

-- Rebar summary by diameter
CREATE VIEW v_rebar_by_diameter AS
SELECT 
    date,
    supplier,
    q8_kg, q10_kg, q12_kg, q14_kg, q16_kg, 
    q18_kg, q20_kg, q22_kg, q25_kg, q28_kg, q32_kg,
    total_weight_kg
FROM rebar_logs
ORDER BY date DESC;

-- Mesh summary by type
CREATE VIEW v_mesh_by_type AS
SELECT 
    mesh_type,
    supplier,
    COUNT(*) as delivery_count,
    SUM(piece_count) as total_pieces,
    SUM(weight_kg) as total_weight_kg
FROM mesh_logs
GROUP BY mesh_type, supplier
ORDER BY mesh_type, supplier;

-- ============================================
-- ROW LEVEL SECURITY (RLS) - Optional
-- ============================================

-- Enable RLS on tables (uncomment if using Supabase Auth)
-- ALTER TABLE concrete_logs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE rebar_logs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE mesh_logs ENABLE ROW LEVEL SECURITY;

-- Create policies (example - adjust based on your auth setup)
-- CREATE POLICY "Allow all operations for authenticated users" 
--     ON concrete_logs FOR ALL 
--     USING (auth.role() = 'authenticated');

-- ============================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================

-- Insert sample concrete record
INSERT INTO concrete_logs (date, supplier, waybill_no, concrete_class, delivery_method, quantity_m3, location_block)
VALUES 
    ('2024-11-21', 'ÖZYURT BETON', '12345', 'C30', 'POMPALI', 15.5, 'GK1'),
    ('2024-11-21', 'ALBAYRAK BETON', '14001', 'C25', 'MİKSERLİ', 12.0, 'GK2');

-- Insert sample rebar record
INSERT INTO rebar_logs (date, supplier, waybill_no, project_stage, q8_kg, q10_kg, q12_kg, total_weight_kg)
VALUES 
    ('2024-11-21', 'ŞAHİN DEMİR', 'D-001', '3.ETAP', 500, 750, 1000, 2250);

-- Insert sample mesh record
INSERT INTO mesh_logs (date, supplier, waybill_no, mesh_type, dimensions, piece_count, weight_kg)
VALUES 
    ('2024-11-21', 'DOFER', 'M-001', 'Q', '215x500', 50, 1250.5);

-- ============================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================

COMMENT ON TABLE concrete_logs IS 'Concrete delivery tracking with supplier and location details';
COMMENT ON TABLE rebar_logs IS 'Rebar delivery tracking with diameter-specific weights';
COMMENT ON TABLE mesh_logs IS 'Steel mesh delivery tracking with type and dimensions';

COMMENT ON COLUMN concrete_logs.quantity_m3 IS 'Quantity in cubic meters';
COMMENT ON COLUMN rebar_logs.total_weight_kg IS 'Total weight in kilograms (sum of all diameters)';
COMMENT ON COLUMN mesh_logs.piece_count IS 'Number of mesh pieces delivered';

-- ============================================
-- UTILITY FUNCTIONS
-- ============================================

-- Function to calculate total rebar weight from individual diameters
CREATE OR REPLACE FUNCTION calculate_rebar_total(
    p_q8 FLOAT, p_q10 FLOAT, p_q12 FLOAT, p_q14 FLOAT, 
    p_q16 FLOAT, p_q18 FLOAT, p_q20 FLOAT, p_q22 FLOAT, 
    p_q25 FLOAT, p_q28 FLOAT, p_q32 FLOAT
)
RETURNS FLOAT AS $$
BEGIN
    RETURN COALESCE(p_q8, 0) + COALESCE(p_q10, 0) + COALESCE(p_q12, 0) + 
           COALESCE(p_q14, 0) + COALESCE(p_q16, 0) + COALESCE(p_q18, 0) + 
           COALESCE(p_q20, 0) + COALESCE(p_q22, 0) + COALESCE(p_q25, 0) + 
           COALESCE(p_q28, 0) + COALESCE(p_q32, 0);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Check if tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('concrete_logs', 'rebar_logs', 'mesh_logs');

-- Check record counts
SELECT 
    (SELECT COUNT(*) FROM concrete_logs) as concrete_count,
    (SELECT COUNT(*) FROM rebar_logs) as rebar_count,
    (SELECT COUNT(*) FROM mesh_logs) as mesh_count;

-- ============================================
-- NOTES
-- ============================================

/*
1. Run this script in your Supabase SQL Editor
2. Make sure to enable UUID extension first
3. Adjust RLS policies based on your authentication needs
4. Indexes are created for common query patterns
5. Views provide pre-aggregated analytics data
6. Triggers automatically update updated_at timestamps
7. Constraints prevent duplicate waybill numbers per supplier
*/


