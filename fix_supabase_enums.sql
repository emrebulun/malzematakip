-- Fix Supabase Enum Issues
-- Run this in Supabase SQL Editor

-- Change concrete_class from enum to TEXT (to accept all values)
ALTER TABLE concrete_logs 
ALTER COLUMN concrete_class TYPE TEXT;

-- Change delivery_method from enum to TEXT
ALTER TABLE concrete_logs 
ALTER COLUMN delivery_method TYPE TEXT;

-- Verify changes
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'concrete_logs' 
AND column_name IN ('concrete_class', 'delivery_method');

