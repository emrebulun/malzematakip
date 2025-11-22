-- ============================================
-- Construction Material Management System
-- Database Schema - PostgreSQL
-- Version: 2.0.0
-- Author: Senior Database Architect
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- ENUMS (Type Definitions)
-- ============================================

CREATE TYPE user_role AS ENUM ('admin', 'site_manager', 'warehouse_staff', 'viewer');
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended');

CREATE TYPE concrete_class AS ENUM ('C16', 'C20', 'C25', 'C30', 'C35', 'C40', 'GRO', 'ŞAP');
CREATE TYPE delivery_method AS ENUM ('POMPALI', 'MİKSERLİ');

CREATE TYPE rebar_diameter AS ENUM ('Q8', 'Q10', 'Q12', 'Q14', 'Q16', 'Q18', 'Q20', 'Q22', 'Q25', 'Q28', 'Q32');

CREATE TYPE mesh_type AS ENUM ('Q', 'R', 'TR');

CREATE TYPE supplier_type AS ENUM ('concrete', 'rebar', 'mesh', 'mixed');

-- ============================================
-- CORE TABLES
-- ============================================

-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'viewer',
    status user_status NOT NULL DEFAULT 'active',
    phone VARCHAR(20),
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);

-- Suppliers Table
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    supplier_type supplier_type NOT NULL,
    tax_number VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255),
    contact_person VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_suppliers_name ON suppliers(name);
CREATE INDEX idx_suppliers_code ON suppliers(code);
CREATE INDEX idx_suppliers_type ON suppliers(supplier_type);
CREATE INDEX idx_suppliers_active ON suppliers(is_active);

-- Projects/Phases Table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    phase VARCHAR(100), -- e.g., "3.ETAP"
    block VARCHAR(100), -- e.g., "GK1", "GK2"
    location TEXT,
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    budget_concrete DECIMAL(15,2),
    budget_rebar DECIMAL(15,2),
    budget_mesh DECIMAL(15,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_projects_code ON projects(code);
CREATE INDEX idx_projects_phase ON projects(phase);
CREATE INDEX idx_projects_block ON projects(block);
CREATE INDEX idx_projects_active ON projects(is_active);

-- ============================================
-- CONCRETE MODULE
-- ============================================

CREATE TABLE concrete_deliveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    waybill_no VARCHAR(50) NOT NULL,
    invoice_no VARCHAR(50),
    delivery_date DATE NOT NULL,
    delivery_time TIME,
    
    supplier_id UUID NOT NULL REFERENCES suppliers(id) ON DELETE RESTRICT,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    
    concrete_class concrete_class NOT NULL,
    delivery_method delivery_method NOT NULL,
    
    quantity_m3 DECIMAL(10,2) NOT NULL CHECK (quantity_m3 > 0),
    unit_price DECIMAL(10,2),
    total_price DECIMAL(15,2) GENERATED ALWAYS AS (quantity_m3 * COALESCE(unit_price, 0)) STORED,
    
    -- Weighing information
    first_weight DECIMAL(10,2),
    second_weight DECIMAL(10,2),
    weight_difference DECIMAL(10,2),
    
    responsible_person VARCHAR(255),
    notes TEXT,
    
    -- Metadata
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    
    CONSTRAINT unique_concrete_waybill UNIQUE(waybill_no, supplier_id)
);

CREATE INDEX idx_concrete_waybill ON concrete_deliveries(waybill_no);
CREATE INDEX idx_concrete_date ON concrete_deliveries(delivery_date DESC);
CREATE INDEX idx_concrete_supplier ON concrete_deliveries(supplier_id);
CREATE INDEX idx_concrete_project ON concrete_deliveries(project_id);
CREATE INDEX idx_concrete_class ON concrete_deliveries(concrete_class);
CREATE INDEX idx_concrete_verified ON concrete_deliveries(is_verified);

-- ============================================
-- REBAR/IRON MODULE (Normalized)
-- ============================================

-- Parent Table: Iron Deliveries
CREATE TABLE rebar_deliveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    waybill_no VARCHAR(50) NOT NULL,
    invoice_no VARCHAR(50),
    delivery_date DATE NOT NULL,
    
    supplier_id UUID NOT NULL REFERENCES suppliers(id) ON DELETE RESTRICT,
    manufacturer VARCHAR(255), -- Actual producer (e.g., Kardemir, İçdaş)
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    
    phase VARCHAR(100), -- e.g., "3.ETAP"
    
    total_weight_kg DECIMAL(12,2) NOT NULL CHECK (total_weight_kg >= 0),
    total_price DECIMAL(15,2),
    
    notes TEXT,
    
    -- Metadata
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    
    CONSTRAINT unique_rebar_waybill UNIQUE(waybill_no, supplier_id)
);

CREATE INDEX idx_rebar_waybill ON rebar_deliveries(waybill_no);
CREATE INDEX idx_rebar_date ON rebar_deliveries(delivery_date DESC);
CREATE INDEX idx_rebar_supplier ON rebar_deliveries(supplier_id);
CREATE INDEX idx_rebar_project ON rebar_deliveries(project_id);
CREATE INDEX idx_rebar_phase ON rebar_deliveries(phase);

-- Child Table: Iron Delivery Items (Normalized by Diameter)
CREATE TABLE rebar_delivery_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    delivery_id UUID NOT NULL REFERENCES rebar_deliveries(id) ON DELETE CASCADE,
    
    diameter rebar_diameter NOT NULL,
    quantity_kg DECIMAL(10,2) NOT NULL CHECK (quantity_kg > 0),
    unit_price DECIMAL(10,2),
    total_price DECIMAL(15,2) GENERATED ALWAYS AS (quantity_kg * COALESCE(unit_price, 0)) STORED,
    
    -- Optional: Track if it's regular or filament (filmaşin)
    is_filament BOOLEAN DEFAULT FALSE,
    
    notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_delivery_diameter UNIQUE(delivery_id, diameter, is_filament)
);

CREATE INDEX idx_rebar_items_delivery ON rebar_delivery_items(delivery_id);
CREATE INDEX idx_rebar_items_diameter ON rebar_delivery_items(diameter);

-- ============================================
-- STEEL MESH MODULE
-- ============================================

CREATE TABLE mesh_deliveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    waybill_no VARCHAR(50) NOT NULL,
    invoice_no VARCHAR(50),
    delivery_date DATE NOT NULL,
    
    supplier_id UUID NOT NULL REFERENCES suppliers(id) ON DELETE RESTRICT,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    
    phase VARCHAR(100),
    mesh_type mesh_type NOT NULL,
    
    -- Dimensions
    length_cm DECIMAL(8,2),
    width_cm DECIMAL(8,2),
    dimensions_text VARCHAR(100), -- e.g., "215x500" for flexibility
    
    -- Bar specifications
    longitudinal_bar_diameter VARCHAR(10),
    transverse_bar_diameter VARCHAR(10),
    longitudinal_spacing DECIMAL(6,2),
    transverse_spacing DECIMAL(6,2),
    
    -- Quantities
    quantity_pieces INTEGER NOT NULL CHECK (quantity_pieces > 0),
    theoretical_weight_kg DECIMAL(10,2), -- Calculated weight per piece
    total_weight_kg DECIMAL(12,2) NOT NULL CHECK (total_weight_kg > 0),
    
    unit_price DECIMAL(10,2),
    total_price DECIMAL(15,2) GENERATED ALWAYS AS (total_weight_kg * COALESCE(unit_price, 0)) STORED,
    
    usage_location VARCHAR(255), -- Where it will be used (e.g., "SS", "GK1")
    
    notes TEXT,
    
    -- Metadata
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    
    CONSTRAINT unique_mesh_waybill UNIQUE(waybill_no, supplier_id)
);

CREATE INDEX idx_mesh_waybill ON mesh_deliveries(waybill_no);
CREATE INDEX idx_mesh_date ON mesh_deliveries(delivery_date DESC);
CREATE INDEX idx_mesh_supplier ON mesh_deliveries(supplier_id);
CREATE INDEX idx_mesh_project ON mesh_deliveries(project_id);
CREATE INDEX idx_mesh_type ON mesh_deliveries(mesh_type);

-- ============================================
-- AUDIT & ACTIVITY LOG
-- ============================================

CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL, -- e.g., 'CREATE', 'UPDATE', 'DELETE', 'VERIFY'
    entity_type VARCHAR(50) NOT NULL, -- e.g., 'concrete_delivery', 'rebar_delivery'
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activity_user ON activity_logs(user_id);
CREATE INDEX idx_activity_entity ON activity_logs(entity_type, entity_id);
CREATE INDEX idx_activity_date ON activity_logs(created_at DESC);

-- ============================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON suppliers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_concrete_updated_at BEFORE UPDATE ON concrete_deliveries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rebar_updated_at BEFORE UPDATE ON rebar_deliveries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rebar_items_updated_at BEFORE UPDATE ON rebar_delivery_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mesh_updated_at BEFORE UPDATE ON mesh_deliveries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS FOR ANALYTICS
-- ============================================

-- Concrete Summary by Project
CREATE VIEW v_concrete_summary_by_project AS
SELECT 
    p.id as project_id,
    p.name as project_name,
    p.code as project_code,
    cd.concrete_class,
    COUNT(*) as delivery_count,
    SUM(cd.quantity_m3) as total_quantity_m3,
    SUM(cd.total_price) as total_cost,
    MIN(cd.delivery_date) as first_delivery,
    MAX(cd.delivery_date) as last_delivery
FROM concrete_deliveries cd
LEFT JOIN projects p ON cd.project_id = p.id
GROUP BY p.id, p.name, p.code, cd.concrete_class;

-- Rebar Summary by Diameter
CREATE VIEW v_rebar_summary_by_diameter AS
SELECT 
    rd.supplier_id,
    s.name as supplier_name,
    rdi.diameter,
    COUNT(DISTINCT rd.id) as delivery_count,
    SUM(rdi.quantity_kg) as total_quantity_kg,
    SUM(rdi.total_price) as total_cost,
    AVG(rdi.unit_price) as avg_unit_price
FROM rebar_deliveries rd
JOIN rebar_delivery_items rdi ON rd.id = rdi.delivery_id
JOIN suppliers s ON rd.supplier_id = s.id
GROUP BY rd.supplier_id, s.name, rdi.diameter;

-- Mesh Summary by Type
CREATE VIEW v_mesh_summary_by_type AS
SELECT 
    md.mesh_type,
    s.name as supplier_name,
    COUNT(*) as delivery_count,
    SUM(md.quantity_pieces) as total_pieces,
    SUM(md.total_weight_kg) as total_weight_kg,
    SUM(md.total_price) as total_cost
FROM mesh_deliveries md
JOIN suppliers s ON md.supplier_id = s.id
GROUP BY md.mesh_type, s.name;

-- ============================================
-- SAMPLE DATA INSERTION
-- ============================================

-- Insert default admin user (password should be hashed in production)
INSERT INTO users (username, email, password_hash, full_name, role) VALUES
('admin', 'admin@santiye997.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIxF3UZinm', 'System Administrator', 'admin');

-- Insert suppliers
INSERT INTO suppliers (name, code, supplier_type) VALUES
('ÖZYURT BETON', 'OZYURT', 'concrete'),
('ALBAYRAK BETON', 'ALBAYRAK', 'concrete'),
('ŞAHİN DEMİR', 'SAHIN', 'rebar'),
('DOFER', 'DOFER', 'mesh'),
('MUREL', 'MUREL', 'mesh');

-- Insert project
INSERT INTO projects (name, code, phase, is_active) VALUES
('Şantiye Proje 997', 'PRJ997', '3.ETAP', TRUE);

-- ============================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================

COMMENT ON TABLE users IS 'System users with role-based access control';
COMMENT ON TABLE suppliers IS 'Material suppliers (concrete, rebar, mesh)';
COMMENT ON TABLE projects IS 'Construction projects/phases/blocks';
COMMENT ON TABLE concrete_deliveries IS 'Concrete delivery records';
COMMENT ON TABLE rebar_deliveries IS 'Rebar delivery parent records';
COMMENT ON TABLE rebar_delivery_items IS 'Normalized rebar items by diameter';
COMMENT ON TABLE mesh_deliveries IS 'Steel mesh delivery records';
COMMENT ON TABLE activity_logs IS 'Audit trail for all system activities';

COMMENT ON COLUMN rebar_delivery_items.is_filament IS 'TRUE if filament (filmaşin) type, FALSE for regular';
COMMENT ON COLUMN concrete_deliveries.total_price IS 'Auto-calculated: quantity_m3 * unit_price';


