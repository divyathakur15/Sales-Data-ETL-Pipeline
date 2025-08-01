# SUPER SIMPLE ETL PIPELINE
# Just save this as etl_simple.py and run it

import pandas as pd
import mysql.connector

# Step 1: Create sample data (no need to download anything)
def create_sample_data():
    """Create sample CSV file automatically"""
    sample_data = {
        'order_id': ['ORD001', 'ORD002', 'ORD003', 'ORD004', 'ORD005'],
        'customer_name': ['John', 'Jane', 'Bob', 'Alice', 'Mike'],
        'product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Phone'],
        'price': [50000, 1500, 3000, 25000, 30000],
        'quantity': [1, 2, 1, 1, 1],
        'date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19']
    }
    
    # Create CSV file
    df = pd.DataFrame(sample_data)
    df.to_csv('sales_data.csv', index=False)
    print("✓ Sample data created: sales_data.csv")
    return df

# Step 2: Simple ETL function
def simple_etl():
    """Run simple ETL process"""
    
    # EXTRACT: Read CSV file
    print("Step 1: Reading data from CSV...")
    df = pd.read_csv('sales_data.csv')
    print(f"✓ Found {len(df)} rows")
    
    # TRANSFORM: Clean data
    print("Step 2: Cleaning data...")
    # Calculate total amount
    df['total_amount'] = df['price'] * df['quantity']
    # Add month column
    df['month'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m')
    print("✓ Data cleaned")
    
    # LOAD: Save to database
    print("Step 3: Saving to database...")
    
    # Database connection (UPDATE WITH YOUR PASSWORD)
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='divya',  # CHANGE THIS TO YOUR MYSQL PASSWORD
        database='sales_etl'
    )
    
    cursor = connection.cursor()
    
    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_sales  (
            id INT AUTO_INCREMENT PRIMARY KEY,
            order_id VARCHAR(50),
            customer_name VARCHAR(100),
            product VARCHAR(100),
            price DECIMAL(10,2),
            quantity INT,
            total_amount DECIMAL(10,2),
            date DATE,
            month VARCHAR(7)
        )
    """)

    # Insert data
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO processed_sales  (order_id, customer_name, product, price, quantity, total_amount, date, month)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row['order_id'], row['customer_name'], row['product'], 
            row['price'], row['quantity'], row['total_amount'], 
            row['date'], row['month']
        ))
    
    connection.commit()
    print(f"✓ Saved {len(df)} rows to database")
    
    # Show some results
    cursor.execute("SELECT * FROM processed_sales LIMIT 3")
    results = cursor.fetchall()
    print("\n📊 Sample data in database:")
    for row in results:
        print(row)
    
    connection.close()
    print("✓ ETL process completed!")

# Step 3: Create database first
def create_database():
    """Create database for the project"""
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='divya'  # CHANGE THIS TO YOUR MYSQL PASSWORD
    )
    
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS sales_etl")
    connection.close()
    print("✓ Database created")

# Main function - Run everything
def main():
    print("🚀 Starting ETL Pipeline...")
    
    try:
        # Step 1: Create database
        create_database()
        
        # Step 2: Create sample data
        create_sample_data()
        
        # Step 3: Run ETL
        simple_etl()
        
        print("\n🎉 All done! Your ETL pipeline is working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure MySQL is running and password is correct")

# Run the program
if __name__ == "__main__":
    main()