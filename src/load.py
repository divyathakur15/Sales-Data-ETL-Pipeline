"""
Load Module
===========
This module handles the LOAD step of ETL.
It saves the transformed data to MySQL database.

What is Load?
- Connecting to the database
- Inserting data into tables
- Handling errors and duplicates
"""

import mysql.connector
from mysql.connector import Error
import pandas as pd
from typing import Optional, List, Tuple


class DatabaseConnection:
    """
    A class to manage MySQL database connections.
    
    Why use a class?
    - Easier to manage connection lifecycle
    - Can reuse connection for multiple operations
    - Better error handling
    
    Usage:
    ------
    with DatabaseConnection(config) as db:
        db.execute_query("SELECT * FROM products")
    """
    
    def __init__(self, config: dict):
        """
        Initialize database connection.
        
        Parameters:
        -----------
        config : dict
            Database configuration with keys:
            - host, port, database, user, password
        """
        self.config = config
        self.connection = None
        self.cursor = None
    
    def __enter__(self):
        """Connect to database (used with 'with' statement)"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Disconnect from database"""
        self.disconnect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
            self.cursor = self.connection.cursor()
            print(f"✅ Connected to MySQL: {self.config['database']}")
        except Error as e:
            print(f"❌ Connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None) -> None:
        """
        Execute a single SQL query (INSERT, UPDATE, DELETE).
        
        Parameters:
        -----------
        query : str
            SQL query to execute
        params : tuple, optional
            Parameters for the query
        """
        self.cursor.execute(query, params)
        self.connection.commit()
    
    def execute_many(self, query: str, data: List[tuple]) -> int:
        """
        Execute a query multiple times with different data.
        This is efficient for bulk inserts.
        
        Parameters:
        -----------
        query : str
            SQL query with %s placeholders
        data : List[tuple]
            List of tuples with data
        
        Returns:
        --------
        int
            Number of rows affected
        """
        self.cursor.executemany(query, data)
        self.connection.commit()
        return self.cursor.rowcount
    
    def fetch_all(self, query: str, params: tuple = None) -> List[tuple]:
        """
        Execute a SELECT query and return all results.
        
        Parameters:
        -----------
        query : str
            SELECT query
        params : tuple, optional
            Query parameters
        
        Returns:
        --------
        List[tuple]
            Query results
        """
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[tuple]:
        """Fetch a single row"""
        self.cursor.execute(query, params)
        return self.cursor.fetchone()


def populate_date_dimension(db: DatabaseConnection, start_year: int = 2023, end_year: int = 2026) -> int:
    """
    Populate the date dimension table with dates.
    
    This creates all dates from start_year to end_year.
    Done in Python because MySQL stored procedure was timing out.
    
    Parameters:
    -----------
    db : DatabaseConnection
        Active database connection
    start_year : int
        Starting year (default 2023)
    end_year : int
        Ending year (default 2026)
    
    Returns:
    --------
    int
        Number of dates inserted
    """
    from datetime import datetime, timedelta
    
    print("📅 LOAD: Populating date dimension...")
    
    # Check if dates already exist
    existing = db.fetch_one("SELECT COUNT(*) FROM dim_date")
    if existing and existing[0] > 0:
        print(f"   Date dimension already has {existing[0]} dates, skipping...")
        return existing[0]
    
    # Generate all dates
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    
    dates_data = []
    current = start_date
    
    while current <= end_date:
        date_id = int(current.strftime('%Y%m%d'))  # e.g., 20240115
        is_weekend = 1 if current.weekday() >= 5 else 0  # Saturday=5, Sunday=6
        
        dates_data.append((
            date_id,
            current.date(),
            current.strftime('%A'),                 # day_name: Monday
            current.day,                             # day_of_month: 15
            current.isoweekday(),                   # day_of_week: 1-7 (Monday=1)
            current.isocalendar()[1],               # week_of_year
            current.month,                           # month_number
            current.strftime('%B'),                  # month_name: January
            (current.month - 1) // 3 + 1,           # quarter_num: 1-4
            f'Q{(current.month - 1) // 3 + 1}',     # quarter_name: Q1
            current.year,                            # year_num
            is_weekend,
            current.strftime('%Y-%m')               # year_month_str: 2024-01
        ))
        
        current += timedelta(days=1)
    
    # Batch insert (much faster than one-by-one)
    insert_query = """
        INSERT IGNORE INTO dim_date 
        (date_id, full_date, day_name, day_of_month, day_of_week, 
         week_of_year, month_number, month_name, quarter_num, quarter_name, 
         year_num, is_weekend, year_month_str)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    # Insert in batches of 100 for efficiency
    batch_size = 100
    total_inserted = 0
    
    for i in range(0, len(dates_data), batch_size):
        batch = dates_data[i:i + batch_size]
        db.cursor.executemany(insert_query, batch)
        db.connection.commit()
        total_inserted += len(batch)
    
    print(f"✅ Date dimension: {total_inserted} dates added ({start_year}-{end_year})")
    return total_inserted


def load_to_staging(db: DatabaseConnection, df: pd.DataFrame) -> int:
    """
    Load raw data to staging table.
    
    Staging is a temporary holding area for raw data.
    We truncate (delete all) before loading new data.
    
    Parameters:
    -----------
    db : DatabaseConnection
        Active database connection
    df : pd.DataFrame
        Data to load
    
    Returns:
    --------
    int
        Number of rows loaded
    """
    
    print("📤 LOAD: Loading data to staging table...")
    
    # Step 1: Truncate staging table (remove old data)
    db.execute_query("TRUNCATE TABLE staging_sales")
    print("   Cleared staging table")
    
    # Step 2: Prepare data for insert
    # Handle different column names (price vs unit_price, date vs order_date)
    price_col = 'price' if 'price' in df.columns else 'unit_price'
    date_col = 'date' if 'date' in df.columns else 'order_date'
    
    # Convert DataFrame rows to list of tuples
    data = []
    for _, row in df.iterrows():
        data.append((
            str(row['order_id']),
            str(row['customer_name']),
            str(row['product']),
            str(row[price_col]),
            str(row['quantity']),
            str(row[date_col]),
            str(row.get('_source_file', 'unknown')),
        ))
    
    # Step 3: Insert data
    insert_query = """
        INSERT INTO staging_sales 
        (order_id, customer_name, product, price, quantity, order_date, source_file)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    rows_inserted = db.execute_many(insert_query, data)
    print(f"✅ Loaded {rows_inserted} rows to staging")
    
    return rows_inserted


def load_dimension_products(db: DatabaseConnection, products_df: pd.DataFrame) -> dict:
    """
    Load products to dimension table.
    
    Uses UPSERT pattern:
    - If product exists: skip (don't update)
    - If product is new: insert
    
    Parameters:
    -----------
    db : DatabaseConnection
        Active database connection
    products_df : pd.DataFrame
        Product data with columns: product_name, unit_price, category
    
    Returns:
    --------
    dict
        Mapping of product_name -> product_id
    """
    
    print("📤 LOAD: Loading products dimension...")
    
    # Track product_name -> product_id mapping
    product_ids = {}
    
    for _, row in products_df.iterrows():
        product_name = row['product_name']
        
        # Check if product already exists
        existing = db.fetch_one(
            "SELECT product_id FROM dim_product WHERE product_name = %s",
            (product_name,)
        )
        
        if existing:
            # Product exists, use existing ID
            product_ids[product_name] = existing[0]
        else:
            # Insert new product
            db.execute_query(
                """
                INSERT INTO dim_product (product_name, category, unit_price)
                VALUES (%s, %s, %s)
                """,
                (product_name, row.get('category', 'General'), row['unit_price'])
            )
            # Get the auto-generated ID
            product_ids[product_name] = db.cursor.lastrowid
    
    print(f"✅ Products: {len(product_ids)} in dimension")
    return product_ids


def load_dimension_customers(db: DatabaseConnection, customers_df: pd.DataFrame) -> dict:
    """
    Load customers to dimension table.
    
    Parameters:
    -----------
    db : DatabaseConnection
        Active database connection
    customers_df : pd.DataFrame
        Customer data with columns: customer_name, segment
    
    Returns:
    --------
    dict
        Mapping of customer_name -> customer_id
    """
    
    print("📤 LOAD: Loading customers dimension...")
    
    customer_ids = {}
    
    for _, row in customers_df.iterrows():
        customer_name = row['customer_name']
        
        # Check if customer already exists
        existing = db.fetch_one(
            "SELECT customer_id FROM dim_customer WHERE customer_name = %s",
            (customer_name,)
        )
        
        if existing:
            customer_ids[customer_name] = existing[0]
        else:
            db.execute_query(
                """
                INSERT INTO dim_customer (customer_name, segment)
                VALUES (%s, %s)
                """,
                (customer_name, row.get('segment', 'Regular'))
            )
            customer_ids[customer_name] = db.cursor.lastrowid
    
    print(f"✅ Customers: {len(customer_ids)} in dimension")
    return customer_ids


def load_fact_sales(db: DatabaseConnection, df: pd.DataFrame, 
                    product_ids: dict, customer_ids: dict) -> int:
    """
    Load sales data to fact table.
    
    This is the main table with all sales transactions.
    Uses dimension IDs instead of names.
    
    Parameters:
    -----------
    db : DatabaseConnection
        Active database connection
    df : pd.DataFrame
        Cleaned sales data
    product_ids : dict
        Mapping of product_name -> product_id
    customer_ids : dict
        Mapping of customer_name -> customer_id
    
    Returns:
    --------
    int
        Number of rows loaded
    """
    
    print("📤 LOAD: Loading fact_sales...")
    
    rows_inserted = 0
    rows_skipped = 0
    
    for _, row in df.iterrows():
        # Get dimension IDs
        product_id = product_ids.get(row['product'])
        customer_id = customer_ids.get(row['customer_name'])
        date_id = int(row['date_id'])
        
        if not product_id or not customer_id:
            print(f"   ⚠️  Skipping {row['order_id']}: missing dimension")
            rows_skipped += 1
            continue
        
        try:
            # Try to insert (will fail if duplicate order_id)
            db.execute_query(
                """
                INSERT INTO fact_sales 
                (order_id, date_id, product_id, customer_id, quantity, unit_price, total_amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    row['order_id'],
                    date_id,
                    product_id,
                    customer_id,
                    int(row['quantity']),
                    float(row['price']),
                    float(row['total_amount'])
                )
            )
            rows_inserted += 1
        except Error as e:
            if "Duplicate entry" in str(e):
                rows_skipped += 1
            else:
                raise
    
    print(f"✅ Loaded {rows_inserted} rows to fact_sales")
    if rows_skipped > 0:
        print(f"   ℹ️  Skipped {rows_skipped} duplicate/invalid rows")
    
    return rows_inserted


# ============================================================
# TEST THE MODULE
# ============================================================
if __name__ == "__main__":
    from config import DB_CONFIG
    
    print("\n" + "="*50)
    print("TESTING LOAD MODULE")
    print("="*50 + "\n")
    
    print("Testing database connection...")
    print(f"Connecting to: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    
    try:
        with DatabaseConnection(DB_CONFIG) as db:
            # Test query
            result = db.fetch_one("SELECT COUNT(*) FROM dim_date")
            print(f"   Dates in dim_date: {result[0]}")
            
            result = db.fetch_one("SELECT COUNT(*) FROM dim_product")
            print(f"   Products in dim_product: {result[0]}")
            
            result = db.fetch_one("SELECT COUNT(*) FROM dim_customer")
            print(f"   Customers in dim_customer: {result[0]}")
            
            result = db.fetch_one("SELECT COUNT(*) FROM fact_sales")
            print(f"   Sales in fact_sales: {result[0]}")
            
        print("\n✅ Database connection test passed!")
        
    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
        print("\n💡 Make sure:")
        print("   1. MySQL is running")
        print("   2. You've run the SQL scripts (01_create_database.sql, 02_create_tables.sql)")
        print("   3. Your password is set in .env file")
