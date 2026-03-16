-- ============================================================
-- STEP 1: CREATE DATABASE
-- ============================================================
-- 
-- What is this script?
-- This creates a new database called "sales_dwh" (dwh = Data Warehouse)
-- 
-- How to run:
-- 1. Open MySQL Workbench
-- 2. Connect to your MySQL server
-- 3. Copy this entire script
-- 4. Click the lightning bolt ⚡ to execute
--
-- ============================================================

-- Create the database (if it doesn't exist)
CREATE DATABASE IF NOT EXISTS sales_dwh;

-- Switch to this database
USE sales_dwh;

-- Show confirmation
SELECT 'Database sales_dwh created successfully!' AS Status;
