"""
Data Quality Module
===================
This module checks data quality after ETL is complete.

Why is Data Quality important?
- Bad data = bad decisions
- Catch errors early
- Build trust in your pipeline
"""

from load import DatabaseConnection


def run_quality_checks(db: DatabaseConnection) -> dict:
    """
    Run all data quality checks.
    
    Parameters:
    -----------
    db : DatabaseConnection
        Active database connection
    
    Returns:
    --------
    dict
        Quality check results
    """
    
    print("\n" + "="*50)
    print("🔍 DATA QUALITY CHECKS")
    print("="*50)
    
    results = {}
    all_passed = True
    
    # =========================================================
    # Check 1: Row counts
    # =========================================================
    print("\n📊 Check 1: Row Counts")
    
    tables = ['staging_sales', 'dim_date', 'dim_product', 'dim_customer', 'fact_sales']
    
    for table in tables:
        count = db.fetch_one(f"SELECT COUNT(*) FROM {table}")[0]
        results[f'{table}_count'] = count
        print(f"   {table}: {count:,} rows")
    
    # =========================================================
    # Check 2: No orphan records in fact table
    # =========================================================
    print("\n📊 Check 2: Referential Integrity")
    
    # Check for fact_sales records without matching dimension
    orphan_products = db.fetch_one("""
        SELECT COUNT(*) FROM fact_sales f 
        LEFT JOIN dim_product p ON f.product_id = p.product_id
        WHERE p.product_id IS NULL
    """)[0]
    
    orphan_customers = db.fetch_one("""
        SELECT COUNT(*) FROM fact_sales f 
        LEFT JOIN dim_customer c ON f.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
    """)[0]
    
    orphan_dates = db.fetch_one("""
        SELECT COUNT(*) FROM fact_sales f 
        LEFT JOIN dim_date d ON f.date_id = d.date_id
        WHERE d.date_id IS NULL
    """)[0]
    
    results['orphan_products'] = orphan_products
    results['orphan_customers'] = orphan_customers
    results['orphan_dates'] = orphan_dates
    
    if orphan_products + orphan_customers + orphan_dates == 0:
        print("   ✅ All fact records have matching dimensions")
    else:
        print(f"   ❌ Orphan records found:")
        print(f"      - Products: {orphan_products}")
        print(f"      - Customers: {orphan_customers}")
        print(f"      - Dates: {orphan_dates}")
        all_passed = False
    
    # =========================================================
    # Check 3: No duplicate orders
    # =========================================================
    print("\n📊 Check 3: Duplicate Orders")
    
    duplicates = db.fetch_one("""
        SELECT COUNT(*) FROM (
            SELECT order_id, COUNT(*) as cnt 
            FROM fact_sales 
            GROUP BY order_id 
            HAVING COUNT(*) > 1
        ) AS dups
    """)[0]
    
    results['duplicate_orders'] = duplicates
    
    if duplicates == 0:
        print("   ✅ No duplicate orders found")
    else:
        print(f"   ❌ Found {duplicates} duplicate order_ids")
        all_passed = False
    
    # =========================================================
    # Check 4: No negative amounts
    # =========================================================
    print("\n📊 Check 4: Negative Values")
    
    negative_amounts = db.fetch_one("""
        SELECT COUNT(*) FROM fact_sales 
        WHERE total_amount < 0 OR quantity < 0 OR unit_price < 0
    """)[0]
    
    results['negative_amounts'] = negative_amounts
    
    if negative_amounts == 0:
        print("   ✅ No negative values found")
    else:
        print(f"   ❌ Found {negative_amounts} rows with negative values")
        all_passed = False
    
    # =========================================================
    # Check 5: Null values in critical columns
    # =========================================================
    print("\n📊 Check 5: Null Values")
    
    null_values = db.fetch_one("""
        SELECT COUNT(*) FROM fact_sales 
        WHERE order_id IS NULL 
           OR product_id IS NULL 
           OR customer_id IS NULL
           OR total_amount IS NULL
    """)[0]
    
    results['null_values'] = null_values
    
    if null_values == 0:
        print("   ✅ No null values in critical columns")
    else:
        print(f"   ❌ Found {null_values} rows with null values")
        all_passed = False
    
    # =========================================================
    # Summary
    # =========================================================
    print("\n" + "="*50)
    
    results['all_passed'] = all_passed
    
    if all_passed:
        print("✅ ALL DATA QUALITY CHECKS PASSED!")
    else:
        print("⚠️  SOME CHECKS FAILED - Review the data")
    
    print("="*50)
    
    return results


def get_summary_stats(db: DatabaseConnection) -> dict:
    """
    Get summary statistics for the data.
    
    Parameters:
    -----------
    db : DatabaseConnection
        Active database connection
    
    Returns:
    --------
    dict
        Summary statistics
    """
    
    print("\n📈 SUMMARY STATISTICS")
    print("-" * 40)
    
    # Total sales
    result = db.fetch_one("""
        SELECT 
            COUNT(*) as total_orders,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_order_value,
            MIN(total_amount) as min_order,
            MAX(total_amount) as max_order
        FROM fact_sales
    """)
    
    if result and result[0]:
        print(f"   Total Orders: {result[0]:,}")
        print(f"   Total Revenue: ₹{result[1]:,.2f}")
        print(f"   Average Order Value: ₹{result[2]:,.2f}")
        print(f"   Smallest Order: ₹{result[3]:,.2f}")
        print(f"   Largest Order: ₹{result[4]:,.2f}")
    
    # Top products
    print("\n   Top 3 Products by Revenue:")
    top_products = db.fetch_all("""
        SELECT p.product_name, SUM(f.total_amount) as revenue
        FROM fact_sales f
        JOIN dim_product p ON f.product_id = p.product_id
        GROUP BY p.product_name
        ORDER BY revenue DESC
        LIMIT 3
    """)
    
    for i, (name, revenue) in enumerate(top_products, 1):
        print(f"      {i}. {name}: ₹{revenue:,.2f}")
    
    return result


# ============================================================
# TEST THE MODULE
# ============================================================
if __name__ == "__main__":
    from config import DB_CONFIG
    
    print("\n" + "="*50)
    print("TESTING DATA QUALITY MODULE")
    print("="*50)
    
    try:
        with DatabaseConnection(DB_CONFIG) as db:
            results = run_quality_checks(db)
            get_summary_stats(db)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure you've run the pipeline first!")
