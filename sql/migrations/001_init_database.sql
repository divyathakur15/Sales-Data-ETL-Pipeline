-- ============================================================================
-- SALES DATA WAREHOUSE - DATABASE INITIALIZATION
-- ============================================================================
-- This script creates the database and schemas for the sales data warehouse.
-- Run this as a superuser (postgres) before running other migration scripts.
-- ============================================================================

-- Create the database
-- Note: You may need to run this separately if using psql
-- CREATE DATABASE sales_dwh;

-- Connect to the database
\c sales_dwh;

-- ============================================================================
-- CREATE SCHEMAS
-- ============================================================================
-- Schema organization:
--   staging: Raw data landing zone (temporary, truncated each run)
--   warehouse: Dimensional model (facts and dimensions)
--   analytics: Aggregated tables and views for reporting
--   audit: Data quality logs and pipeline metadata

CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS warehouse;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS audit;

-- Grant usage on schemas
GRANT USAGE ON SCHEMA staging TO etl_user;
GRANT USAGE ON SCHEMA warehouse TO etl_user;
GRANT USAGE ON SCHEMA analytics TO etl_user;
GRANT USAGE ON SCHEMA audit TO etl_user;

-- Grant all privileges on tables in schemas
ALTER DEFAULT PRIVILEGES IN SCHEMA staging GRANT ALL ON TABLES TO etl_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA warehouse GRANT ALL ON TABLES TO etl_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT ALL ON TABLES TO etl_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA audit GRANT ALL ON TABLES TO etl_user;

COMMENT ON SCHEMA staging IS 'Raw data landing zone - truncated each ETL run';
COMMENT ON SCHEMA warehouse IS 'Dimensional model with facts and dimensions';
COMMENT ON SCHEMA analytics IS 'Aggregated tables and materialized views';
COMMENT ON SCHEMA audit IS 'Data quality logs and pipeline metadata';
