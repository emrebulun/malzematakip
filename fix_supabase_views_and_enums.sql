-- Fix Supabase: Drop Views, Change Enums to TEXT
-- Run this in Supabase SQL Editor

-- Step 1: Drop all views that use concrete_logs
DROP VIEW IF EXISTS v_concrete_by_supplier CASCADE;
DROP VIEW IF EXISTS v_concrete_by_location CASCADE;
DROP VIEW IF EXISTS v_concrete_by_class CASCADE;
DROP VIEW IF EXISTS v_concrete_summary CASCADE;

-- Step 2: Change enum columns to TEXT
ALTER TABLE concrete_logs 
ALTER COLUMN concrete_class TYPE TEXT;

ALTER TABLE concrete_logs 
ALTER COLUMN delivery_method TYPE TEXT;

-- Step 3: Verify changes
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'concrete_logs' 
AND column_name IN ('concrete_class', 'delivery_method');

-- Done! Now you can import all data without enum restrictions

