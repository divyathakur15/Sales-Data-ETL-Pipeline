"""
Main ETL Pipeline
=================
This is the main script that runs the entire ETL pipeline.

How it works:
1. EXTRACT: Read data from CSV files
2. TRANSFORM: Clean and prepare data
3. LOAD: Save to MySQL database
4. QUALITY CHECK: Verify data quality

How to run:
    python src/pipeline.py
    
    Or with a specific file:
    python src/pipeline.py --file data/raw/sales_data.csv
"""

import sys
import os
from datetime import datetime

# Add src directory to path (so we can import our modules)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DB_CONFIG, RAW_DATA_DIR, PROJECT_ROOT
from extract import extract_from_csv, create_sample_data
from transform import clean_sales_data, validate_data, prepare_dimension_data, remove_duplicates
from load import DatabaseConnection, load_to_staging, load_dimension_products, load_dimension_customers, load_fact_sales, populate_date_dimension
from data_quality import run_quality_checks, get_summary_stats


def run_pipeline(source_file: str = None):
    """
    Run the complete ETL pipeline.
    
    Parameters:
    -----------
    source_file : str, optional
        Path to CSV file to process.
        If not provided, uses sample data.
    """
    
    print("\n" + "=" * 60)
    print("🚀 SALES DATA ETL PIPELINE")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # =====================================================
        # STEP 1: EXTRACT
        # =====================================================
        print("\n" + "-" * 40)
        print("STEP 1: EXTRACT")
        print("-" * 40)
        
        if source_file and os.path.exists(source_file):
            # Read from specified file
            raw_data = extract_from_csv(source_file)
        else:
            # Check default location
            default_file = os.path.join(PROJECT_ROOT, 'sales_data.csv')
            if os.path.exists(default_file):
                raw_data = extract_from_csv(default_file)
            else:
                # Create sample data
                print("   No CSV file found. Creating sample data...")
                raw_data = create_sample_data()
        
        print(f"\n   📊 Extracted: {len(raw_data)} rows")
        print("\n   Sample data preview:")
        print(raw_data.head(3).to_string(index=False))
        
        # =====================================================
        # STEP 2: TRANSFORM
        # =====================================================
        print("\n" + "-" * 40)
        print("STEP 2: TRANSFORM")
        print("-" * 40)
        
        # Clean the data
        clean_data = clean_sales_data(raw_data)
        
        # Remove duplicates
        clean_data = remove_duplicates(clean_data)
        
        # Validate data quality
        validation = validate_data(clean_data)
        
        if not validation['overall_passed']:
            print("\n⚠️  Warning: Some validation checks failed")
            print("   Continuing with pipeline (you may want to review data)")
        
        # Prepare dimension data
        dimensions = prepare_dimension_data(clean_data)
        
        print(f"\n   📊 Transformed: {len(clean_data)} rows")
        print("\n   Cleaned data preview:")
        print(clean_data[['order_id', 'customer_name', 'product', 'total_amount', 'date_id']].head(3).to_string(index=False))
        
        # =====================================================
        # STEP 3: LOAD
        # =====================================================
        print("\n" + "-" * 40)
        print("STEP 3: LOAD")
        print("-" * 40)
        
        # Connect to database and load data
        with DatabaseConnection(DB_CONFIG) as db:
            # First, populate date dimension (if not already done)
            populate_date_dimension(db)
            
            # Load to staging (optional, for audit trail)
            staging_rows = load_to_staging(db, raw_data)
            
            # Load dimensions
            product_ids = load_dimension_products(db, dimensions['products'])
            customer_ids = load_dimension_customers(db, dimensions['customers'])
            
            # Load facts
            fact_rows = load_fact_sales(db, clean_data, product_ids, customer_ids)
            
            # =====================================================
            # STEP 4: QUALITY CHECKS
            # =====================================================
            print("\n" + "-" * 40)
            print("STEP 4: QUALITY CHECKS")
            print("-" * 40)
            
            quality_results = run_quality_checks(db)
            
            # Show summary statistics
            get_summary_stats(db)
        
        # =====================================================
        # SUMMARY
        # =====================================================
        print("\n" + "=" * 60)
        print("✅ ETL PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n📊 Summary:")
        print(f"   - Rows extracted: {len(raw_data)}")
        print(f"   - Rows transformed: {len(clean_data)}")
        print(f"   - Rows loaded to staging: {staging_rows}")
        print(f"   - Rows loaded to fact_sales: {fact_rows}")
        print(f"   - Quality checks passed: {'Yes' if quality_results['all_passed'] else 'No'}")
        print("\n💡 Next steps:")
        print("   1. Open MySQL Workbench and run queries from sql/03_useful_queries.sql")
        print("   2. Connect Power BI to MySQL to create visualizations")
        print("   3. Add more data files to data/raw/ and run again")
        print("=" * 60)
        
        return True
        
    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}")
        print("💡 Make sure your CSV file exists")
        return False
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Is MySQL running?")
        print("   2. Did you create the database? (Run sql/01_create_database.sql)")
        print("   3. Did you create the tables? (Run sql/02_create_tables.sql)")
        print("   4. Is your password set in .env file?")
        
        # Print more details for debugging
        import traceback
        print("\n📋 Full error details:")
        traceback.print_exc()
        
        return False


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run Sales ETL Pipeline')
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Path to CSV file to process'
    )
    
    args = parser.parse_args()
    
    # Run the pipeline
    success = run_pipeline(source_file=args.file)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
