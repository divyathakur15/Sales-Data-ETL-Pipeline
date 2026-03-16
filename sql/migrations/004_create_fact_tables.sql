-- ============================================================================
-- FACT TABLES - Sales Transactions
-- ============================================================================
-- Fact tables contain measurable, quantitative data (metrics/measures).
-- Grain: One row per order line item.
-- Partitioned by date for query performance.
-- ============================================================================

-- ============================================================================
-- FACT: Sales Transactions
-- ============================================================================
DROP TABLE IF EXISTS warehouse.fact_sales CASCADE;

CREATE TABLE warehouse.fact_sales (
    -- Surrogate key
    sales_sk            BIGSERIAL PRIMARY KEY,
    
    -- Degenerate dimension (order identifier)
    order_id            VARCHAR(100) NOT NULL,
    order_line_number   SMALLINT DEFAULT 1,
    
    -- Foreign keys to dimensions
    date_key            INTEGER NOT NULL REFERENCES warehouse.dim_date(date_key),
    product_sk          INTEGER NOT NULL REFERENCES warehouse.dim_product(product_sk),
    customer_sk         INTEGER NOT NULL REFERENCES warehouse.dim_customer(customer_sk),
    status_sk           INTEGER REFERENCES warehouse.dim_order_status(status_sk),
    
    -- Measures (additive facts)
    quantity            INTEGER NOT NULL,
    unit_price          DECIMAL(12, 2) NOT NULL,
    unit_cost           DECIMAL(12, 2) DEFAULT 0,
    discount_amount     DECIMAL(12, 2) DEFAULT 0,
    tax_amount          DECIMAL(12, 2) DEFAULT 0,
    
    -- Calculated measures
    gross_amount        DECIMAL(12, 2) NOT NULL,  -- quantity * unit_price
    net_amount          DECIMAL(12, 2) NOT NULL,  -- gross - discount + tax
    profit_amount       DECIMAL(12, 2),           -- net - (quantity * unit_cost)
    
    -- Semi-additive facts
    order_date          DATE NOT NULL,
    ship_date           DATE,
    delivery_date       DATE,
    
    -- ETL metadata
    batch_id            VARCHAR(50),
    source_system       VARCHAR(50) DEFAULT 'CSV',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (order_date);

-- Create partitions for each year (extend as needed)
CREATE TABLE warehouse.fact_sales_2023 PARTITION OF warehouse.fact_sales
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');
    
CREATE TABLE warehouse.fact_sales_2024 PARTITION OF warehouse.fact_sales
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
    
CREATE TABLE warehouse.fact_sales_2025 PARTITION OF warehouse.fact_sales
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE warehouse.fact_sales_2026 PARTITION OF warehouse.fact_sales
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

-- Indexes for common query patterns
CREATE INDEX idx_fact_sales_date_key ON warehouse.fact_sales(date_key);
CREATE INDEX idx_fact_sales_product_sk ON warehouse.fact_sales(product_sk);
CREATE INDEX idx_fact_sales_customer_sk ON warehouse.fact_sales(customer_sk);
CREATE INDEX idx_fact_sales_order_id ON warehouse.fact_sales(order_id);
CREATE INDEX idx_fact_sales_order_date ON warehouse.fact_sales(order_date);

-- Composite indexes for common analytical queries
CREATE INDEX idx_fact_sales_date_product ON warehouse.fact_sales(date_key, product_sk);
CREATE INDEX idx_fact_sales_date_customer ON warehouse.fact_sales(date_key, customer_sk);

-- Unique constraint to prevent duplicate loads
CREATE UNIQUE INDEX idx_fact_sales_unique_order 
    ON warehouse.fact_sales(order_id, order_line_number, product_sk);

COMMENT ON TABLE warehouse.fact_sales IS 'Fact table for sales transactions - grain: one row per order line item';

-- ============================================================================
-- FACT: Daily Sales Aggregate (For faster dashboard queries)
-- ============================================================================
DROP TABLE IF EXISTS warehouse.fact_daily_sales_agg CASCADE;

CREATE TABLE warehouse.fact_daily_sales_agg (
    -- Keys
    date_key            INTEGER NOT NULL REFERENCES warehouse.dim_date(date_key),
    product_sk          INTEGER NOT NULL REFERENCES warehouse.dim_product(product_sk),
    customer_segment    VARCHAR(50),
    
    -- Aggregated measures
    order_count         INTEGER NOT NULL DEFAULT 0,
    total_quantity      INTEGER NOT NULL DEFAULT 0,
    total_gross_amount  DECIMAL(14, 2) NOT NULL DEFAULT 0,
    total_net_amount    DECIMAL(14, 2) NOT NULL DEFAULT 0,
    total_profit        DECIMAL(14, 2) DEFAULT 0,
    total_discount      DECIMAL(14, 2) DEFAULT 0,
    
    -- Derived metrics
    avg_order_value     DECIMAL(12, 2),
    avg_quantity        DECIMAL(10, 2),
    
    -- Metadata
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (date_key, product_sk, customer_segment)
);

CREATE INDEX idx_daily_agg_date ON warehouse.fact_daily_sales_agg(date_key);
CREATE INDEX idx_daily_agg_product ON warehouse.fact_daily_sales_agg(product_sk);

COMMENT ON TABLE warehouse.fact_daily_sales_agg IS 'Pre-aggregated daily sales for dashboard performance';
