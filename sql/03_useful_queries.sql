-- ============================================================
-- STEP 3: USEFUL QUERIES FOR ANALYTICS & POWER BI
-- ============================================================
-- 
-- These queries help you analyze your sales data.
-- You can use them in:
--   1. MySQL Workbench to see results
--   2. Power BI to create visualizations
--
-- ============================================================

USE sales_dwh;

-- ============================================================
-- BASIC QUERIES (Start Here)
-- ============================================================

-- Query 1: View all sales with customer and product names
-- This is a JOIN query - combines data from multiple tables
SELECT 
    f.order_id,
    c.customer_name,
    p.product_name,
    d.full_date AS order_date,
    f.quantity,
    f.unit_price,
    f.total_amount
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
JOIN dim_product p ON f.product_id = p.product_id
JOIN dim_date d ON f.date_id = d.date_id
ORDER BY d.full_date DESC;


-- Query 2: Total sales by product
SELECT 
    p.product_name,
    COUNT(*) AS number_of_orders,
    SUM(f.quantity) AS total_quantity_sold,
    SUM(f.total_amount) AS total_revenue
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_revenue DESC;


-- Query 3: Total sales by customer
SELECT 
    c.customer_name,
    COUNT(*) AS number_of_orders,
    SUM(f.total_amount) AS total_spent
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.customer_name
ORDER BY total_spent DESC;


-- ============================================================
-- INTERMEDIATE QUERIES (Time-Based Analysis)
-- ============================================================

-- Query 4: Sales by month
SELECT 
    d.year_month,
    d.month_name,
    COUNT(*) AS number_of_orders,
    SUM(f.total_amount) AS monthly_revenue
FROM fact_sales f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY d.year_month, d.month_name
ORDER BY d.year_month;


-- Query 5: Sales by day of week (which day has most sales?)
SELECT 
    d.day_name,
    COUNT(*) AS number_of_orders,
    SUM(f.total_amount) AS total_revenue,
    AVG(f.total_amount) AS average_order_value
FROM fact_sales f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY d.day_name, d.day_of_week
ORDER BY d.day_of_week;


-- Query 6: Weekend vs Weekday sales
SELECT 
    CASE WHEN d.is_weekend THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    COUNT(*) AS number_of_orders,
    SUM(f.total_amount) AS total_revenue
FROM fact_sales f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY d.is_weekend;


-- ============================================================
-- ADVANCED QUERIES (Business Metrics)
-- ============================================================

-- Query 7: Average Order Value (AOV) - Key business metric!
SELECT 
    ROUND(AVG(total_amount), 2) AS average_order_value,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    COUNT(*) AS total_orders
FROM fact_sales;


-- Query 8: Top 3 products by revenue
SELECT 
    p.product_name,
    SUM(f.total_amount) AS total_revenue
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_revenue DESC
LIMIT 3;


-- Query 9: Sales growth by month (compare to previous month)
-- This uses a window function - advanced but very useful!
WITH monthly_sales AS (
    SELECT 
        d.year_month,
        SUM(f.total_amount) AS revenue
    FROM fact_sales f
    JOIN dim_date d ON f.date_id = d.date_id
    GROUP BY d.year_month
)
SELECT 
    year_month,
    revenue,
    LAG(revenue) OVER (ORDER BY year_month) AS previous_month_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY year_month)) / 
        LAG(revenue) OVER (ORDER BY year_month) * 100, 
        2
    ) AS growth_percentage
FROM monthly_sales
ORDER BY year_month;


-- Query 10: Customer segmentation by total purchases
SELECT 
    c.customer_name,
    SUM(f.total_amount) AS total_spent,
    CASE 
        WHEN SUM(f.total_amount) >= 50000 THEN 'VIP'
        WHEN SUM(f.total_amount) >= 20000 THEN 'Premium'
        ELSE 'Regular'
    END AS customer_segment
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.customer_name
ORDER BY total_spent DESC;


-- ============================================================
-- DATA QUALITY CHECKS
-- ============================================================

-- Check 1: Count records in each table
SELECT 'staging_sales' AS table_name, COUNT(*) AS row_count FROM staging_sales
UNION ALL
SELECT 'dim_date', COUNT(*) FROM dim_date
UNION ALL
SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL
SELECT 'dim_customer', COUNT(*) FROM dim_customer
UNION ALL
SELECT 'fact_sales', COUNT(*) FROM fact_sales;


-- Check 2: Find duplicate orders (should return 0 rows)
SELECT order_id, COUNT(*) AS occurrences
FROM fact_sales
GROUP BY order_id
HAVING COUNT(*) > 1;


-- Check 3: Check for NULL values in critical columns
SELECT 
    SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) AS null_order_ids,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_customer_ids,
    SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END) AS null_product_ids,
    SUM(CASE WHEN total_amount IS NULL THEN 1 ELSE 0 END) AS null_amounts
FROM fact_sales;


-- ============================================================
-- POWER BI READY VIEWS
-- ============================================================
-- You can create these as VIEWS for easy access from Power BI

-- View 1: Sales Summary (ready for dashboard)
DROP VIEW IF EXISTS vw_sales_summary;

CREATE VIEW vw_sales_summary AS
SELECT 
    f.sales_id,
    f.order_id,
    d.full_date AS order_date,
    d.year,
    d.month_name,
    d.quarter_name,
    d.day_name,
    d.is_weekend,
    c.customer_name,
    c.segment AS customer_segment,
    p.product_name,
    p.category AS product_category,
    f.quantity,
    f.unit_price,
    f.total_amount
FROM fact_sales f
JOIN dim_date d ON f.date_id = d.date_id
JOIN dim_customer c ON f.customer_id = c.customer_id
JOIN dim_product p ON f.product_id = p.product_id;

-- Test the view
SELECT * FROM vw_sales_summary;
