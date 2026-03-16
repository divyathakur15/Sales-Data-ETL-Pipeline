-- ============================================================
-- STEP 2: CREATE ALL TABLES
-- ============================================================
-- 
-- This script creates the STAR SCHEMA for our data warehouse:
--   - 1 Staging Table (temporary storage for raw data)
--   - 3 Dimension Tables (dim_date, dim_product, dim_customer)
--   - 1 Fact Table (fact_sales)
--
-- ============================================================

USE sales_dwh;

-- ============================================================
-- STAGING TABLE
-- ============================================================
-- What is staging?
-- It's a temporary table where we first load raw data from CSV.
-- We clean it here before moving to final tables.
-- 
-- Why use staging?
-- 1. Can accept "dirty" data (all VARCHAR to avoid errors)
-- 2. Easy to truncate and reload
-- 3. Keeps raw data separate from clean data

DROP TABLE IF EXISTS staging_sales;

CREATE TABLE staging_sales (
    -- All columns are VARCHAR to accept any data format
    -- We'll convert to proper types during Transform step
    order_id        VARCHAR(100),
    customer_name   VARCHAR(255),
    product         VARCHAR(255),
    price           VARCHAR(50),    -- VARCHAR, not DECIMAL (raw data might have errors)
    quantity        VARCHAR(50),    -- VARCHAR, not INT (raw data might have errors)
    order_date      VARCHAR(50),    -- VARCHAR, not DATE (different date formats possible)
    
    -- Metadata: Track when and from where data was loaded
    source_file     VARCHAR(255),
    loaded_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT 'staging_sales table created!' AS Status;


-- ============================================================
-- DIMENSION TABLE: dim_date
-- ============================================================
-- What is a Date Dimension?
-- Instead of storing dates in the fact table, we create a separate
-- table with all date-related attributes pre-calculated.
--
-- Benefits:
-- 1. Easy to filter by month, quarter, year
-- 2. Easy to check if weekend/holiday
-- 3. No need to calculate date parts in every query

DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_date (
    date_id         INT PRIMARY KEY,            -- Format: YYYYMMDD (e.g., 20240115)
    full_date       DATE NOT NULL,              -- The actual date
    
    -- Day information
    day_name        VARCHAR(10),                -- Monday, Tuesday, etc.
    day_of_month    INT,                        -- 1-31
    day_of_week     INT,                        -- 1-7 (1=Monday)
    
    -- Week information
    week_of_year    INT,                        -- 1-52
    
    -- Month information
    month_number    INT,                        -- 1-12
    month_name      VARCHAR(10),                -- January, February, etc.
    
    -- Quarter information
    quarter_num     INT,                        -- 1-4
    quarter_name    VARCHAR(2),                 -- Q1, Q2, Q3, Q4
    
    -- Year information
    year_num        INT,                        -- 2024, 2025, etc.
    
    -- Useful flags
    is_weekend      TINYINT(1) DEFAULT 0,
    
    -- For easy filtering
    year_month_str  VARCHAR(7)
);

SELECT 'dim_date table created!' AS Status;


-- ============================================================
-- DIMENSION TABLE: dim_product
-- ============================================================
-- Stores information about products
-- One row per unique product

DROP TABLE IF EXISTS dim_product;

CREATE TABLE dim_product (
    product_id          INT AUTO_INCREMENT PRIMARY KEY,     -- Unique ID (auto-generated)
    product_name        VARCHAR(255) NOT NULL,              -- Laptop, Mouse, etc.
    category            VARCHAR(100),                       -- Electronics, Accessories, etc.
    unit_price          DECIMAL(10, 2),                     -- Standard selling price
    
    -- Timestamps for tracking changes
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Ensure no duplicate product names
    UNIQUE KEY unique_product_name (product_name)
);

SELECT 'dim_product table created!' AS Status;


-- ============================================================
-- DIMENSION TABLE: dim_customer
-- ============================================================
-- Stores information about customers
-- One row per unique customer

DROP TABLE IF EXISTS dim_customer;

CREATE TABLE dim_customer (
    customer_id         INT AUTO_INCREMENT PRIMARY KEY,     -- Unique ID (auto-generated)
    customer_name       VARCHAR(255) NOT NULL,              -- John, Jane, etc.
    email               VARCHAR(255),                       -- Optional: email address
    city                VARCHAR(100),                       -- Optional: city
    segment             VARCHAR(50) DEFAULT 'Regular',      -- Regular, Premium, VIP
    
    -- Timestamps for tracking changes
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Ensure no duplicate customer names (in real world, use email)
    UNIQUE KEY unique_customer_name (customer_name)
);

SELECT 'dim_customer table created!' AS Status;


-- ============================================================
-- FACT TABLE: fact_sales
-- ============================================================
-- This is the MAIN table - contains all sales transactions
-- Each row = one order
-- 
-- Notice:
-- - Foreign keys link to dimension tables
-- - Contains numbers (measures) we want to analyze
-- - No text descriptions (those are in dimensions)

DROP TABLE IF EXISTS fact_sales;

CREATE TABLE fact_sales (
    -- Primary key
    sales_id            INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Order identifier (from source data)
    order_id            VARCHAR(100) NOT NULL,
    
    -- Foreign keys to dimension tables
    -- These link to the dimension tables above
    date_id             INT NOT NULL,
    product_id          INT NOT NULL,
    customer_id         INT NOT NULL,
    
    -- Measures (numbers we want to analyze)
    quantity            INT NOT NULL,
    unit_price          DECIMAL(10, 2) NOT NULL,
    total_amount        DECIMAL(12, 2) NOT NULL,
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicate orders
    UNIQUE KEY unique_order (order_id),
    
    -- Foreign key constraints (ensure data integrity)
    -- If you delete a product, you can't have orphan sales
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    
    -- Index for faster queries
    INDEX idx_date (date_id),
    INDEX idx_product (product_id),
    INDEX idx_customer (customer_id)
);

SELECT 'fact_sales table created!' AS Status;


-- ============================================================
-- POPULATE dim_date (Pre-fill date dimension)
-- ============================================================
-- Date dimension will be populated by Python ETL pipeline
-- This avoids timeout issues in MySQL Workbench

SELECT 'All tables created successfully!' AS Status;
SELECT 'Date dimension will be populated by Python ETL pipeline' AS Note;


-- ============================================================
-- SUMMARY: Show all tables created
-- ============================================================
SELECT 
    table_name,
    table_rows,
    ROUND((data_length + index_length) / 1024, 2) AS size_kb
FROM information_schema.tables
WHERE table_schema = 'sales_dwh'
ORDER BY table_name;
