-- ============================================
-- Construction Material Tracking System
-- Supabase (PostgreSQL) Schema - CLEAN INSTALL
-- ============================================

-- ============================================
-- STEP 1: DROP EXISTING OBJECTS (if any)
-- ============================================

-- Drop tables first (due to dependencies)
DROP TABLE IF EXISTS concrete_logs CASCADE;
DROP TABLE IF EXISTS rebar_logs CASCADE;
DROP TABLE IF EXISTS mesh_logs CASCADE;

-- Drop views
DROP VIEW IF EXISTS v_concrete_by_supplier CASCADE;
DROP VIEW IF EXISTS v_concrete_by_location CASCADE;
DROP VIEW IF EXISTS v_rebar_by_diameter CASCADE;
DROP VIEW IF EXISTS v_mesh_by_type CASCADE;

-- Drop functions
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
DROP FUNCTION IF EXISTS calculate_rebar_total(FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT) CASCADE;

-- Drop enums
DROP TYPE IF EXISTS concrete_class_enum CASCADE;
DROP TYPE IF EXISTS delivery_method_enum CASCADE;
DROP TYPE IF EXISTS mesh_type_enum CASCADE;

-- ============================================
-- STEP 2: ENABLE UUID EXTENSION
-- ============================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- STEP 3: CREATE ENUMS
-- ============================================

CREATE TYPE concrete_class_enum AS ENUM (
    'C16', 'C20', 'C25', 'C30', 'C35', 'C40', 'GRO', 'ŞAP'
);

CREATE TYPE delivery_method_enum AS ENUM (
    'POMPALI', 'MİKSERLİ'
);

CREATE TYPE mesh_type_enum AS ENUM (
    'Q', 'R', 'TR'
);

-- ============================================
-- STEP 4: CREATE TABLES
-- ============================================

-- TABLE 1: CONCRETE LOGS
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
    
    CONSTRAINT unique_concrete_waybill UNIQUE(waybill_no, supplier)
);

-- TABLE 2: REBAR LOGS
CREATE TABLE rebar_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    supplier TEXT NOT NULL,
    waybill_no TEXT NOT NULL,
    project_stage TEXT,
    manufacturer TEXT,
    
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
    
    total_weight_kg FLOAT NOT NULL CHECK (total_weight_kg >= 0),
    
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_rebar_waybill UNIQUE(waybill_no, supplier)
);

-- TABLE 3: MESH LOGS
CREATE TABLE mesh_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    supplier TEXT NOT NULL,
    waybill_no TEXT NOT NULL,
    mesh_type mesh_type_enum NOT NULL,
    dimensions TEXT,
    piece_count INTEGER NOT NULL CHECK (piece_count > 0),
    weight_kg FLOAT NOT NULL CHECK (weight_kg > 0),
    usage_location TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_mesh_waybill UNIQUE(waybill_no, supplier)
);

-- ============================================
-- STEP 5: CREATE INDEXES
-- ============================================

-- Concrete indexes
CREATE INDEX idx_concrete_date ON concrete_logs(date DESC);
CREATE INDEX idx_concrete_supplier ON concrete_logs(supplier);
CREATE INDEX idx_concrete_location ON concrete_logs(location_block);
CREATE INDEX idx_concrete_created ON concrete_logs(created_at DESC);

-- Rebar indexes
CREATE INDEX idx_rebar_date ON rebar_logs(date DESC);
CREATE INDEX idx_rebar_supplier ON rebar_logs(supplier);
CREATE INDEX idx_rebar_stage ON rebar_logs(project_stage);
CREATE INDEX idx_rebar_created ON rebar_logs(created_at DESC);

-- Mesh indexes
CREATE INDEX idx_mesh_date ON mesh_logs(date DESC);
CREATE INDEX idx_mesh_supplier ON mesh_logs(supplier);
CREATE INDEX idx_mesh_type ON mesh_logs(mesh_type);
CREATE INDEX idx_mesh_created ON mesh_logs(created_at DESC);

-- ============================================
-- STEP 6: CREATE TRIGGERS
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

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
-- STEP 7: CREATE VIEWS
-- ============================================

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

CREATE VIEW v_rebar_by_diameter AS
SELECT 
    date,
    supplier,
    q8_kg, q10_kg, q12_kg, q14_kg, q16_kg, 
    q18_kg, q20_kg, q22_kg, q25_kg, q28_kg, q32_kg,
    total_weight_kg
FROM rebar_logs
ORDER BY date DESC;

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
-- STEP 8: INSERT SAMPLE DATA
-- ============================================

INSERT INTO concrete_logs (date, supplier, waybill_no, concrete_class, delivery_method, quantity_m3, location_block)
VALUES 
    ('2024-11-21', 'ÖZYURT BETON', '12345', 'C30', 'POMPALI', 15.5, 'GK1'),
    ('2024-11-21', 'ALBAYRAK BETON', '14001', 'C25', 'MİKSERLİ', 12.0, 'GK2');

INSERT INTO rebar_logs (date, supplier, waybill_no, project_stage, q8_kg, q10_kg, q12_kg, total_weight_kg)
VALUES 
    ('2024-11-21', 'ŞAHİN DEMİR', 'D-001', '3.ETAP', 500, 750, 1000, 2250);

INSERT INTO mesh_logs (date, supplier, waybill_no, mesh_type, dimensions, piece_count, weight_kg)
VALUES 
    ('2024-11-21', 'DOFER', 'M-001', 'Q', '215x500', 50, 1250.5);

-- ============================================
-- STEP 9: VERIFICATION
-- ============================================

-- Check tables exist
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
AND table_name IN ('concrete_logs', 'rebar_logs', 'mesh_logs')
ORDER BY table_name;

-- Check record counts
SELECT 
    'concrete_logs' as table_name,
    COUNT(*) as record_count
FROM concrete_logs
UNION ALL
SELECT 
    'rebar_logs',
    COUNT(*)
FROM rebar_logs
UNION ALL
SELECT 
    'mesh_logs',
    COUNT(*)
FROM mesh_logs;

-- ============================================
-- SUCCESS MESSAGE
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '✅ Schema created successfully!';
    RAISE NOTICE '✅ 3 tables created: concrete_logs, rebar_logs, mesh_logs';
    RAISE NOTICE '✅ Sample data inserted';
    RAISE NOTICE '✅ Ready to use!';
END $$;





