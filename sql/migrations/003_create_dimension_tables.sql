-- ============================================================================
-- DIMENSION TABLES - Star Schema
-- ============================================================================
-- Dimension tables contain descriptive attributes for slicing and dicing facts.
-- Using Surrogate Keys (SK) for flexibility and slowly changing dimensions.
-- ============================================================================

-- ============================================================================
-- DIMENSION: Date (Pre-populated calendar dimension)
-- ============================================================================
DROP TABLE IF EXISTS warehouse.dim_date CASCADE;

CREATE TABLE warehouse.dim_date (
    date_key            INTEGER PRIMARY KEY,  -- YYYYMMDD format
    full_date           DATE NOT NULL UNIQUE,
    
    -- Date attributes
    day_of_week         SMALLINT NOT NULL,    -- 1-7 (Monday=1)
    day_of_week_name    VARCHAR(10) NOT NULL,
    day_of_month        SMALLINT NOT NULL,
    day_of_year         SMALLINT NOT NULL,
    
    -- Week attributes
    week_of_year        SMALLINT NOT NULL,
    week_start_date     DATE NOT NULL,
    week_end_date       DATE NOT NULL,
    
    -- Month attributes
    month_number        SMALLINT NOT NULL,
    month_name          VARCHAR(10) NOT NULL,
    month_short_name    VARCHAR(3) NOT NULL,
    year_month          VARCHAR(7) NOT NULL,  -- YYYY-MM
    
    -- Quarter attributes
    quarter_number      SMALLINT NOT NULL,
    quarter_name        VARCHAR(2) NOT NULL,  -- Q1, Q2, Q3, Q4
    year_quarter        VARCHAR(7) NOT NULL,  -- YYYY-Q1
    
    -- Year attributes
    year_number         INTEGER NOT NULL,
    
    -- Fiscal attributes (assuming fiscal year = calendar year)
    fiscal_year         INTEGER NOT NULL,
    fiscal_quarter      SMALLINT NOT NULL,
    
    -- Flags
    is_weekend          BOOLEAN NOT NULL,
    is_holiday          BOOLEAN DEFAULT FALSE,
    is_current_day      BOOLEAN DEFAULT FALSE,
    is_current_month    BOOLEAN DEFAULT FALSE,
    is_current_year     BOOLEAN DEFAULT FALSE
);

-- Indexes for common date queries
CREATE INDEX idx_dim_date_year_month ON warehouse.dim_date(year_month);
CREATE INDEX idx_dim_date_year ON warehouse.dim_date(year_number);
CREATE INDEX idx_dim_date_quarter ON warehouse.dim_date(year_quarter);

COMMENT ON TABLE warehouse.dim_date IS 'Calendar dimension with date attributes for time-based analysis';

-- ============================================================================
-- DIMENSION: Product (SCD Type 2)
-- ============================================================================
DROP TABLE IF EXISTS warehouse.dim_product CASCADE;

CREATE TABLE warehouse.dim_product (
    product_sk          SERIAL PRIMARY KEY,           -- Surrogate key
    product_id          VARCHAR(100) NOT NULL,        -- Natural/business key
    
    -- Product attributes
    product_name        VARCHAR(255) NOT NULL,
    category            VARCHAR(100),
    subcategory         VARCHAR(100),
    brand               VARCHAR(100),
    unit_cost           DECIMAL(12, 2),
    unit_price          DECIMAL(12, 2),
    profit_margin       DECIMAL(5, 4),                -- Calculated: (price-cost)/price
    
    -- SCD Type 2 columns
    effective_start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    effective_end_date   DATE DEFAULT '9999-12-31',
    is_current          BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Audit columns
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Hash for change detection
    row_hash            VARCHAR(64)
);

CREATE INDEX idx_dim_product_natural_key ON warehouse.dim_product(product_id);
CREATE INDEX idx_dim_product_current ON warehouse.dim_product(is_current) WHERE is_current = TRUE;
CREATE INDEX idx_dim_product_category ON warehouse.dim_product(category);

COMMENT ON TABLE warehouse.dim_product IS 'Product dimension with SCD Type 2 for historical tracking';

-- ============================================================================
-- DIMENSION: Customer (SCD Type 2)
-- ============================================================================
DROP TABLE IF EXISTS warehouse.dim_customer CASCADE;

CREATE TABLE warehouse.dim_customer (
    customer_sk         SERIAL PRIMARY KEY,           -- Surrogate key
    customer_id         VARCHAR(100) NOT NULL,        -- Natural/business key
    
    -- Customer attributes
    customer_name       VARCHAR(255) NOT NULL,
    email               VARCHAR(255),
    phone               VARCHAR(50),
    
    -- Address attributes
    address             VARCHAR(500),
    city                VARCHAR(100),
    state               VARCHAR(100),
    country             VARCHAR(100) DEFAULT 'India',
    postal_code         VARCHAR(20),
    
    -- Segmentation
    customer_segment    VARCHAR(50),                  -- Consumer, Corporate, etc.
    
    -- SCD Type 2 columns
    effective_start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    effective_end_date   DATE DEFAULT '9999-12-31',
    is_current          BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Audit columns
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Hash for change detection
    row_hash            VARCHAR(64)
);

CREATE INDEX idx_dim_customer_natural_key ON warehouse.dim_customer(customer_id);
CREATE INDEX idx_dim_customer_current ON warehouse.dim_customer(is_current) WHERE is_current = TRUE;
CREATE INDEX idx_dim_customer_segment ON warehouse.dim_customer(customer_segment);
CREATE INDEX idx_dim_customer_city ON warehouse.dim_customer(city);

COMMENT ON TABLE warehouse.dim_customer IS 'Customer dimension with SCD Type 2 for historical tracking';

-- ============================================================================
-- DIMENSION: Order Status (Static/Reference dimension)
-- ============================================================================
DROP TABLE IF EXISTS warehouse.dim_order_status CASCADE;

CREATE TABLE warehouse.dim_order_status (
    status_sk           SERIAL PRIMARY KEY,
    status_code         VARCHAR(20) NOT NULL UNIQUE,
    status_name         VARCHAR(50) NOT NULL,
    status_description  VARCHAR(255),
    is_active           BOOLEAN DEFAULT TRUE
);

-- Insert standard order statuses
INSERT INTO warehouse.dim_order_status (status_code, status_name, status_description) VALUES
    ('NEW', 'New', 'Order has been placed'),
    ('CONFIRMED', 'Confirmed', 'Order has been confirmed'),
    ('PROCESSING', 'Processing', 'Order is being processed'),
    ('SHIPPED', 'Shipped', 'Order has been shipped'),
    ('DELIVERED', 'Delivered', 'Order has been delivered'),
    ('CANCELLED', 'Cancelled', 'Order has been cancelled'),
    ('RETURNED', 'Returned', 'Order has been returned'),
    ('REFUNDED', 'Refunded', 'Order has been refunded');

COMMENT ON TABLE warehouse.dim_order_status IS 'Reference dimension for order statuses';
