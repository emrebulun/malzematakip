-- Run this in Supabase SQL Editor to remove unique constraint

-- Drop the unique constraint on concrete_logs
ALTER TABLE concrete_logs 
DROP CONSTRAINT IF EXISTS unique_concrete_waybill;

-- Verify
SELECT conname, contype 
FROM pg_constraint 
WHERE conrelid = 'concrete_logs'::regclass;

-- After running this, re-run the import script



