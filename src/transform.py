"""
Transform Module
================
This module handles the TRANSFORM step of ETL.
It cleans, validates, and enriches the data.

What is Transform?
- Cleaning: Fix errors, handle missing values
- Validating: Check data quality
- Enriching: Add calculated columns
- Standardizing: Make data consistent
"""

import pandas as pd
from datetime import datetime
import hashlib


def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the raw sales data.
    
    Steps:
    1. Handle missing values
    2. Convert data types
    3. Standardize text
    4. Add calculated columns
    
    Parameters:
    -----------
    df : pd.DataFrame
        Raw sales data from extract step
    
    Returns:
    --------
    pd.DataFrame
        Cleaned sales data
    """
    
    print("🔧 TRANSFORM: Cleaning data...")
    
    # Make a copy to avoid modifying original data
    df = df.copy()
    
    # Track initial row count
    initial_rows = len(df)
    
    # ---------------------------------------------------------
    # Step 1: Normalize column names (handle different CSV formats)
    # ---------------------------------------------------------
    print("   Step 1: Normalizing column names...")
    
    # Map alternative column names to standard names
    column_mapping = {
        'unit_price': 'price',
        'order_date': 'date',
        'net_amount': 'total_amount',
    }
    
    # Rename columns if they exist
    for old_name, new_name in column_mapping.items():
        if old_name in df.columns and new_name not in df.columns:
            df = df.rename(columns={old_name: new_name})
            print(f"   Renamed '{old_name}' to '{new_name}'")
    
    # ---------------------------------------------------------
    # Step 2: Handle missing values
    # ---------------------------------------------------------
    print("   Step 2: Handling missing values...")
    
    # Check for nulls
    null_counts = df.isnull().sum()
    if null_counts.any():
        print(f"   ⚠️  Found missing values: {null_counts[null_counts > 0].to_dict()}")
    
    # Drop rows with missing critical fields
    critical_columns = ['order_id', 'customer_name', 'product', 'price', 'quantity']
    # Only check columns that exist
    existing_critical = [col for col in critical_columns if col in df.columns]
    df = df.dropna(subset=existing_critical)
    
    rows_dropped = initial_rows - len(df)
    if rows_dropped > 0:
        print(f"   ⚠️  Dropped {rows_dropped} rows with missing critical values")
    
    # ---------------------------------------------------------
    # Step 3: Convert data types
    # ---------------------------------------------------------
    print("   Step 3: Converting data types...")
    
    # Convert price and quantity to numbers
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # ---------------------------------------------------------
    # Step 4: Standardize text
    # ---------------------------------------------------------
    print("   Step 4: Standardizing text...")
    
    # Trim whitespace and capitalize names
    df['customer_name'] = df['customer_name'].str.strip().str.title()
    df['product'] = df['product'].str.strip().str.title()
    
    # Standardize order_id (uppercase)
    df['order_id'] = df['order_id'].str.strip().str.upper()
    
    # ---------------------------------------------------------
    # Step 5: Add calculated columns
    # ---------------------------------------------------------
    print("   Step 5: Adding calculated columns...")
    
    # Calculate total amount (if not already present)
    if 'total_amount' not in df.columns:
        df['total_amount'] = df['price'] * df['quantity']
    
    # Extract date parts (for the date dimension)
    df['date_id'] = df['date'].dt.strftime('%Y%m%d').astype(int)
    df['year_month'] = df['date'].dt.strftime('%Y-%m')
    
    print(f"✅ Cleaned {len(df)} rows")
    
    return df


def validate_data(df: pd.DataFrame) -> dict:
    """
    Validate data quality and return a report.
    
    Checks:
    1. No duplicate order_ids
    2. No negative prices or quantities
    3. All dates are valid
    4. No nulls in critical columns
    
    Parameters:
    -----------
    df : pd.DataFrame
        Cleaned sales data
    
    Returns:
    --------
    dict
        Validation report with pass/fail for each check
    """
    
    print("🔍 TRANSFORM: Validating data quality...")
    
    validation_results = {}
    all_passed = True
    
    # Check 1: No duplicate order_ids
    duplicates = df['order_id'].duplicated().sum()
    validation_results['no_duplicate_orders'] = {
        'passed': duplicates == 0,
        'message': f"Found {duplicates} duplicate order_ids" if duplicates > 0 else "No duplicates"
    }
    if duplicates > 0:
        all_passed = False
        print(f"   ⚠️  Warning: {duplicates} duplicate orders found")
    
    # Check 2: No negative values
    negative_prices = (df['price'] < 0).sum()
    negative_quantities = (df['quantity'] < 0).sum()
    validation_results['no_negative_values'] = {
        'passed': negative_prices == 0 and negative_quantities == 0,
        'message': f"Negative prices: {negative_prices}, Negative quantities: {negative_quantities}"
    }
    if negative_prices > 0 or negative_quantities > 0:
        all_passed = False
    
    # Check 3: All dates are valid
    invalid_dates = df['date'].isna().sum()
    validation_results['valid_dates'] = {
        'passed': invalid_dates == 0,
        'message': f"Found {invalid_dates} invalid dates" if invalid_dates > 0 else "All dates valid"
    }
    if invalid_dates > 0:
        all_passed = False
    
    # Check 4: No nulls in critical columns
    critical_nulls = df[['order_id', 'customer_name', 'product', 'price', 'quantity']].isnull().sum().sum()
    validation_results['no_critical_nulls'] = {
        'passed': critical_nulls == 0,
        'message': f"Found {critical_nulls} null values" if critical_nulls > 0 else "No null values"
    }
    if critical_nulls > 0:
        all_passed = False
    
    # Summary
    validation_results['overall_passed'] = all_passed
    
    if all_passed:
        print("✅ All validation checks passed!")
    else:
        print("⚠️  Some validation checks failed. Review the data.")
    
    return validation_results


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate records.
    
    For duplicate order_ids, keep the first occurrence.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Sales data
    
    Returns:
    --------
    pd.DataFrame
        Data with duplicates removed
    """
    
    initial_count = len(df)
    df = df.drop_duplicates(subset=['order_id'], keep='first')
    removed = initial_count - len(df)
    
    if removed > 0:
        print(f"   Removed {removed} duplicate orders")
    
    return df


def prepare_dimension_data(df: pd.DataFrame) -> dict:
    """
    Prepare data for dimension tables.
    
    Extract unique values for each dimension:
    - Products
    - Customers
    
    Parameters:
    -----------
    df : pd.DataFrame
        Cleaned sales data
    
    Returns:
    --------
    dict
        Dictionary with dimension data
    """
    
    print("📊 TRANSFORM: Preparing dimension data...")
    
    dimensions = {}
    
    # ---------------------------------------------------------
    # Product dimension
    # ---------------------------------------------------------
    # Get columns that exist for products
    product_cols = ['product', 'price']
    if 'category' in df.columns:
        product_cols.append('category')
    
    products = df[product_cols].copy()
    products = products.drop_duplicates(subset=['product'])
    products = products.rename(columns={
        'product': 'product_name',
        'price': 'unit_price'
    })
    
    # Add category if not present
    if 'category' not in products.columns:
        products['category'] = 'General'
    
    dimensions['products'] = products
    print(f"   Products: {len(products)} unique")
    
    # ---------------------------------------------------------
    # Customer dimension
    # ---------------------------------------------------------
    # Get columns that exist for customers
    customer_cols = ['customer_name']
    if 'customer_segment' in df.columns:
        customer_cols.append('customer_segment')
    
    customers = df[customer_cols].copy()
    customers = customers.drop_duplicates(subset=['customer_name'])
    
    # Rename segment column if it exists
    if 'customer_segment' in customers.columns:
        customers = customers.rename(columns={'customer_segment': 'segment'})
    else:
        customers['segment'] = 'Regular'
    
    dimensions['customers'] = customers
    print(f"   Customers: {len(customers)} unique")
    
    print("✅ Dimension data prepared")
    
    return dimensions


# ============================================================
# TEST THE MODULE
# ============================================================
if __name__ == "__main__":
    from extract import create_sample_data
    
    print("\n" + "="*50)
    print("TESTING TRANSFORM MODULE")
    print("="*50 + "\n")
    
    # Get sample data
    raw_df = create_sample_data()
    
    print("\nRaw data:")
    print(raw_df.head())
    
    # Clean the data
    clean_df = clean_sales_data(raw_df)
    
    print("\nCleaned data:")
    print(clean_df.head())
    
    # Validate
    validation = validate_data(clean_df)
    print("\nValidation results:")
    for check, result in validation.items():
        if check != 'overall_passed':
            status = "✅" if result['passed'] else "❌"
            print(f"  {status} {check}: {result['message']}")
    
    # Prepare dimensions
    dimensions = prepare_dimension_data(clean_df)
    
    print("\nProducts dimension:")
    print(dimensions['products'])
    
    print("\nCustomers dimension:")
    print(dimensions['customers'])
