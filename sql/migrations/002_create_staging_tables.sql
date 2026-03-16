-- ============================================================================
-- STAGING TABLES - Raw Data Landing Zone
-- ============================================================================
-- These tables receive raw data from source systems.
-- They are typically truncated before each load.
-- Minimal constraints to accept "dirty" data for cleaning in transform step.
-- ============================================================================

-- Drop existing staging tables
DROP TABLE IF EXISTS staging.stg_sales CASCADE;
DROP TABLE IF EXISTS staging.stg_products CASCADE;
DROP TABLE IF EXISTS staging.stg_customers CASCADE;

-- ============================================================================
-- STAGING: Sales Transactions
-- ============================================================================
CREATE TABLE staging.stg_sales (
    -- Source columns (raw data as-is)
    order_id            VARCHAR(100),
    customer_name       VARCHAR(255),
    product             VARCHAR(255),
    price               VARCHAR(50),      -- VARCHAR to handle dirty data
    quantity            VARCHAR(50),      -- VARCHAR to handle dirty data
    order_date          VARCHAR(50),      -- VARCHAR to handle various date formats
    
    -- ETL metadata
    source_file         VARCHAR(500),
    loaded_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    batch_id            VARCHAR(50)
);

-- Index for deduplication checks
CREATE INDEX idx_stg_sales_order_id ON staging.stg_sales(order_id);
CREATE INDEX idx_stg_sales_batch_id ON staging.stg_sales(batch_id);

COMMENT ON TABLE staging.stg_sales IS 'Staging table for raw sales data from CSV files';

-- ============================================================================
-- STAGING: Products (for future expansion)
-- ============================================================================
CREATE TABLE staging.stg_products (
    product_id          VARCHAR(100),
    product_name        VARCHAR(255),
    category            VARCHAR(100),
    subcategory         VARCHAR(100),
    brand               VARCHAR(100),
    unit_cost           VARCHAR(50),
    unit_price          VARCHAR(50),
    
    -- ETL metadata
    source_file         VARCHAR(500),
    loaded_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    batch_id            VARCHAR(50)
);

CREATE INDEX idx_stg_products_product_id ON staging.stg_products(product_id);

COMMENT ON TABLE staging.stg_products IS 'Staging table for product master data';

-- ============================================================================
-- STAGING: Customers (for future expansion)
-- ============================================================================
CREATE TABLE staging.stg_customers (
    customer_id         VARCHAR(100),
    customer_name       VARCHAR(255),
    email               VARCHAR(255),
    phone               VARCHAR(50),
    address             VARCHAR(500),
    city                VARCHAR(100),
    state               VARCHAR(100),
    country             VARCHAR(100),
    postal_code         VARCHAR(20),
    segment             VARCHAR(50),
    
    -- ETL metadata
    source_file         VARCHAR(500),
    loaded_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    batch_id            VARCHAR(50)
);

CREATE INDEX idx_stg_customers_customer_id ON staging.stg_customers(customer_id);

COMMENT ON TABLE staging.stg_customers IS 'Staging table for customer master data';
