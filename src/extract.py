"""
Extract Module
==============
This module handles the EXTRACT step of ETL.
It reads data from source files (CSV) and returns it as a pandas DataFrame.

What is Extract?
- Getting data from the source (files, APIs, databases)
- Not modifying the data - just reading it
"""

import os
import pandas as pd
from datetime import datetime


def extract_from_csv(file_path: str) -> pd.DataFrame:
    """
    Read data from a CSV file.
    
    Parameters:
    -----------
    file_path : str
        Path to the CSV file (e.g., 'data/raw/sales_data.csv')
    
    Returns:
    --------
    pd.DataFrame
        The data from the CSV file
    
    Example:
    --------
    >>> df = extract_from_csv('data/raw/sales_data.csv')
    >>> print(df.head())
    """
    
    print(f"📂 EXTRACT: Reading file {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ File not found: {file_path}")
    
    # Read CSV file
    df = pd.read_csv(file_path)
    
    # Add metadata columns (useful for tracking)
    df['_source_file'] = os.path.basename(file_path)  # Just the filename
    df['_loaded_at'] = datetime.now()                  # When we loaded it
    
    print(f"✅ Extracted {len(df)} rows from {os.path.basename(file_path)}")
    
    return df


def extract_all_csv_from_folder(folder_path: str) -> pd.DataFrame:
    """
    Read all CSV files from a folder and combine them.
    
    This is useful when you have multiple files to process:
    - sales_january.csv
    - sales_february.csv
    - sales_march.csv
    
    Parameters:
    -----------
    folder_path : str
        Path to folder containing CSV files
    
    Returns:
    --------
    pd.DataFrame
        Combined data from all CSV files
    """
    
    print(f"📂 EXTRACT: Reading all CSV files from {folder_path}")
    
    # Find all CSV files in the folder
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    if not csv_files:
        raise FileNotFoundError(f"❌ No CSV files found in {folder_path}")
    
    print(f"   Found {len(csv_files)} CSV file(s)")
    
    # Read each file and combine
    all_dataframes = []
    
    for filename in csv_files:
        file_path = os.path.join(folder_path, filename)
        df = extract_from_csv(file_path)
        all_dataframes.append(df)
    
    # Combine all dataframes into one
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    print(f"✅ Total: {len(combined_df)} rows from {len(csv_files)} files")
    
    return combined_df


def create_sample_data() -> pd.DataFrame:
    """
    Create sample sales data for testing.
    
    This is useful when you don't have real data yet.
    In real projects, this would read from actual files.
    
    Returns:
    --------
    pd.DataFrame
        Sample sales data
    """
    
    print("📝 Creating sample sales data...")
    
    sample_data = {
        'order_id': ['ORD001', 'ORD002', 'ORD003', 'ORD004', 'ORD005',
                     'ORD006', 'ORD007', 'ORD008', 'ORD009', 'ORD010'],
        'customer_name': ['John', 'Jane', 'Bob', 'Alice', 'Mike',
                          'Sarah', 'Tom', 'Emma', 'John', 'Jane'],  # John and Jane buy again!
        'product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Phone',
                    'Tablet', 'Laptop', 'Mouse', 'Headphones', 'Webcam'],
        'price': [50000, 1500, 3000, 25000, 30000,
                  20000, 55000, 1200, 5000, 3500],
        'quantity': [1, 2, 1, 1, 1, 1, 1, 3, 2, 1],
        'date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19',
                 '2024-01-20', '2024-01-22', '2024-01-23', '2024-01-25', '2024-01-28']
    }
    
    df = pd.DataFrame(sample_data)
    
    # Add metadata
    df['_source_file'] = 'sample_data'
    df['_loaded_at'] = datetime.now()
    
    print(f"✅ Created {len(df)} sample rows")
    
    return df


# ============================================================
# TEST THE MODULE
# ============================================================
if __name__ == "__main__":
    # Test creating sample data
    print("\n" + "="*50)
    print("TESTING EXTRACT MODULE")
    print("="*50 + "\n")
    
    df = create_sample_data()
    print("\nSample data preview:")
    print(df.head())
    print("\nColumn types:")
    print(df.dtypes)
