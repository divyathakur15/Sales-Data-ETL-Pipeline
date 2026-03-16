"""
🏭 SALES DATA GENERATOR
========================
This script creates realistic sales data for:
- ETL pipeline testing
- Power BI dashboards
- Python visualizations

Features:
- Multiple products with categories
- Customer segments (Regular, Premium, VIP)
- Regional data (cities)
- Seasonal sales patterns
- Returns and discounts

How to run:
    python src/generate_sample_data.py
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# ============================================================
# CONFIGURATION - CUSTOMIZE YOUR DATA HERE
# ============================================================

# How many orders to generate?
NUMBER_OF_ORDERS = 1000  # Good for dashboards!

# Date range
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)  # 2 years of data

# Random seed for reproducibility (same data each time)
RANDOM_SEED = 42

# ============================================================
# PRODUCTS CATALOG
# ============================================================
PRODUCTS = {
    # Electronics
    'Laptop': {'price': 55000, 'cost': 45000, 'category': 'Electronics', 'subcategory': 'Computers'},
    'Desktop PC': {'price': 45000, 'cost': 35000, 'category': 'Electronics', 'subcategory': 'Computers'},
    'Phone': {'price': 30000, 'cost': 22000, 'category': 'Electronics', 'subcategory': 'Mobile'},
    'Tablet': {'price': 35000, 'cost': 27000, 'category': 'Electronics', 'subcategory': 'Mobile'},
    'Smart Watch': {'price': 15000, 'cost': 10000, 'category': 'Electronics', 'subcategory': 'Wearables'},
    'Monitor': {'price': 25000, 'cost': 18000, 'category': 'Electronics', 'subcategory': 'Displays'},
    'TV': {'price': 40000, 'cost': 30000, 'category': 'Electronics', 'subcategory': 'Displays'},
    
    # Accessories
    'Mouse': {'price': 1500, 'cost': 800, 'category': 'Accessories', 'subcategory': 'Input Devices'},
    'Keyboard': {'price': 3000, 'cost': 1800, 'category': 'Accessories', 'subcategory': 'Input Devices'},
    'Headphones': {'price': 5000, 'cost': 3000, 'category': 'Accessories', 'subcategory': 'Audio'},
    'Earbuds': {'price': 3500, 'cost': 2000, 'category': 'Accessories', 'subcategory': 'Audio'},
    'Webcam': {'price': 4000, 'cost': 2500, 'category': 'Accessories', 'subcategory': 'Video'},
    'Mouse Pad': {'price': 800, 'cost': 300, 'category': 'Accessories', 'subcategory': 'Input Devices'},
    'Laptop Stand': {'price': 2500, 'cost': 1500, 'category': 'Accessories', 'subcategory': 'Ergonomics'},
    
    # Storage
    'External HDD 1TB': {'price': 5000, 'cost': 3500, 'category': 'Storage', 'subcategory': 'Hard Drives'},
    'External SSD 500GB': {'price': 6000, 'cost': 4000, 'category': 'Storage', 'subcategory': 'Solid State'},
    'Pen Drive 64GB': {'price': 800, 'cost': 400, 'category': 'Storage', 'subcategory': 'Flash Storage'},
    'Memory Card 128GB': {'price': 1200, 'cost': 700, 'category': 'Storage', 'subcategory': 'Flash Storage'},
    
    # Networking
    'WiFi Router': {'price': 3500, 'cost': 2200, 'category': 'Networking', 'subcategory': 'Routers'},
    'USB Hub': {'price': 1500, 'cost': 800, 'category': 'Networking', 'subcategory': 'Connectivity'},
    'Ethernet Cable': {'price': 500, 'cost': 200, 'category': 'Networking', 'subcategory': 'Cables'},
}

# ============================================================
# CUSTOMERS
# ============================================================
CUSTOMER_FIRST_NAMES = [
    'Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Reyansh', 'Ayaan',
    'Ananya', 'Diya', 'Aadhya', 'Pihu', 'Priya', 'Sara', 'Myra', 'Isha',
    'Rahul', 'Amit', 'Vikram', 'Rohit', 'Neha', 'Pooja', 'Sneha', 'Divya',
    'John', 'Emma', 'James', 'Olivia', 'William', 'Sophia', 'Michael', 'Ava',
]

CUSTOMER_LAST_NAMES = [
    'Sharma', 'Verma', 'Gupta', 'Singh', 'Kumar', 'Patel', 'Shah', 'Joshi',
    'Reddy', 'Nair', 'Menon', 'Iyer', 'Rao', 'Pillai', 'Das', 'Bose',
    'Smith', 'Johnson', 'Brown', 'Wilson', 'Miller', 'Davis', 'Anderson', 'Taylor',
]

# ============================================================
# LOCATIONS (for regional analysis)
# ============================================================
REGIONS = {
    'North': {
        'cities': ['Delhi', 'Jaipur', 'Lucknow', 'Chandigarh'],
        'weight': 0.25  # 25% of orders
    },
    'South': {
        'cities': ['Bangalore', 'Chennai', 'Hyderabad', 'Kochi'],
        'weight': 0.30  # 30% of orders
    },
    'West': {
        'cities': ['Mumbai', 'Pune', 'Ahmedabad', 'Surat'],
        'weight': 0.30  # 30% of orders
    },
    'East': {
        'cities': ['Kolkata', 'Bhubaneswar', 'Patna', 'Guwahati'],
        'weight': 0.15  # 15% of orders
    },
}

# ============================================================
# CUSTOMER SEGMENTS
# ============================================================
SEGMENTS = {
    'Regular': {'weight': 0.60, 'discount_range': (0, 5)},      # 60% customers
    'Premium': {'weight': 0.30, 'discount_range': (5, 10)},     # 30% customers
    'VIP': {'weight': 0.10, 'discount_range': (10, 20)},        # 10% customers
}

# ============================================================
# PAYMENT METHODS
# ============================================================
PAYMENT_METHODS = {
    'Credit Card': 0.30,
    'Debit Card': 0.25,
    'UPI': 0.25,
    'Net Banking': 0.10,
    'Cash on Delivery': 0.10,
}

# ============================================================
# ORDER STATUS
# ============================================================
ORDER_STATUSES = {
    'Delivered': 0.85,
    'Shipped': 0.05,
    'Processing': 0.03,
    'Cancelled': 0.05,
    'Returned': 0.02,
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def set_seed():
    """Set random seed for reproducibility."""
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)


def generate_customer_id() -> str:
    """Generate unique customer ID."""
    return f"CUST{random.randint(1000, 9999)}"


def generate_customer_name() -> str:
    """Generate random customer name."""
    first = random.choice(CUSTOMER_FIRST_NAMES)
    last = random.choice(CUSTOMER_LAST_NAMES)
    return f"{first} {last}"


def get_region_and_city() -> tuple:
    """Get random region and city based on weights."""
    region = random.choices(
        list(REGIONS.keys()),
        weights=[r['weight'] for r in REGIONS.values()]
    )[0]
    city = random.choice(REGIONS[region]['cities'])
    return region, city


def get_segment() -> str:
    """Get random customer segment based on weights."""
    return random.choices(
        list(SEGMENTS.keys()),
        weights=[s['weight'] for s in SEGMENTS.values()]
    )[0]


def get_payment_method() -> str:
    """Get random payment method based on weights."""
    return random.choices(
        list(PAYMENT_METHODS.keys()),
        weights=list(PAYMENT_METHODS.values())
    )[0]


def get_order_status() -> str:
    """Get random order status based on weights."""
    return random.choices(
        list(ORDER_STATUSES.keys()),
        weights=list(ORDER_STATUSES.values())
    )[0]


def generate_date_with_seasonality(start: datetime, end: datetime) -> datetime:
    """
    Generate date with seasonal patterns.
    More sales in:
    - Festival season (Oct-Nov)
    - End of year (Dec)
    - Summer sales (May-Jun)
    """
    # Generate random date
    days_between = (end - start).days
    random_day = random.randint(0, days_between)
    date = start + timedelta(days=random_day)
    
    # Apply seasonality (higher chance of keeping dates in peak months)
    month = date.month
    
    # Peak months have higher probability
    peak_months = {10: 1.5, 11: 1.8, 12: 1.6, 5: 1.3, 6: 1.3, 1: 1.2}
    
    if month in peak_months:
        if random.random() < 0.7:  # 70% chance to keep peak month date
            return date
    
    return date


def calculate_discount(segment: str, base_price: float) -> float:
    """Calculate discount based on customer segment."""
    min_disc, max_disc = SEGMENTS[segment]['discount_range']
    discount_percent = random.uniform(min_disc, max_disc)
    return round(base_price * discount_percent / 100, 2)


# ============================================================
# MAIN DATA GENERATION
# ============================================================

def generate_sales_data(num_orders: int) -> pd.DataFrame:
    """Generate comprehensive sales data."""
    
    print(f"🔄 Generating {num_orders} orders...")
    
    set_seed()
    
    # Create a pool of customers (customers can order multiple times)
    num_customers = num_orders // 3  # Average 3 orders per customer
    customers = {}
    for _ in range(num_customers):
        cust_id = generate_customer_id()
        customers[cust_id] = {
            'name': generate_customer_name(),
            'segment': get_segment(),
            'region': get_region_and_city(),
        }
    
    customer_ids = list(customers.keys())
    product_names = list(PRODUCTS.keys())
    
    data = []
    
    for i in range(1, num_orders + 1):
        # Pick customer (might repeat - realistic!)
        cust_id = random.choice(customer_ids)
        customer = customers[cust_id]
        
        # Pick product
        product_name = random.choice(product_names)
        product = PRODUCTS[product_name]
        
        # Order details
        quantity = random.choices([1, 2, 3, 4, 5], weights=[0.5, 0.25, 0.15, 0.07, 0.03])[0]
        unit_price = product['price']
        unit_cost = product['cost']
        
        # Calculate amounts
        gross_amount = unit_price * quantity
        discount = calculate_discount(customer['segment'], gross_amount)
        tax_rate = 0.18  # 18% GST
        tax_amount = round((gross_amount - discount) * tax_rate, 2)
        net_amount = round(gross_amount - discount + tax_amount, 2)
        profit = round(net_amount - (unit_cost * quantity) - tax_amount, 2)
        
        # Generate date
        order_date = generate_date_with_seasonality(START_DATE, END_DATE)
        
        # Create order
        order = {
            # Order info
            'order_id': f"ORD{i:05d}",
            'order_date': order_date.strftime('%Y-%m-%d'),
            'order_status': get_order_status(),
            
            # Customer info
            'customer_id': cust_id,
            'customer_name': customer['name'],
            'customer_segment': customer['segment'],
            
            # Location info
            'region': customer['region'][0],
            'city': customer['region'][1],
            
            # Product info
            'product': product_name,
            'category': product['category'],
            'subcategory': product['subcategory'],
            
            # Quantity & pricing
            'quantity': quantity,
            'unit_price': unit_price,
            'unit_cost': unit_cost,
            
            # Calculated amounts
            'gross_amount': gross_amount,
            'discount': discount,
            'tax_amount': tax_amount,
            'net_amount': net_amount,
            'profit': profit,
            
            # Payment
            'payment_method': get_payment_method(),
        }
        
        data.append(order)
        
        # Progress indicator
        if i % 200 == 0:
            print(f"   Generated {i}/{num_orders} orders...")
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Sort by date
    df = df.sort_values('order_date').reset_index(drop=True)
    
    return df


def generate_products_master() -> pd.DataFrame:
    """Generate products master data."""
    products_list = []
    for i, (name, details) in enumerate(PRODUCTS.items(), 1):
        products_list.append({
            'product_id': f"PROD{i:03d}",
            'product_name': name,
            'category': details['category'],
            'subcategory': details['subcategory'],
            'unit_price': details['price'],
            'unit_cost': details['cost'],
            'profit_margin': round((details['price'] - details['cost']) / details['price'] * 100, 1),
        })
    return pd.DataFrame(products_list)


def generate_customers_master(sales_df: pd.DataFrame) -> pd.DataFrame:
    """Generate customers master data from sales."""
    customers = sales_df.groupby(['customer_id', 'customer_name', 'customer_segment', 'region', 'city']).agg({
        'order_id': 'count',
        'net_amount': 'sum',
    }).reset_index()
    
    customers.columns = ['customer_id', 'customer_name', 'segment', 'region', 'city', 'total_orders', 'total_spent']
    customers['avg_order_value'] = round(customers['total_spent'] / customers['total_orders'], 2)
    
    return customers


# ============================================================
# SAVE DATA
# ============================================================

def save_data(df: pd.DataFrame, filename: str, folder: str = 'raw') -> str:
    """Save DataFrame to CSV."""
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', folder)
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False)
    
    return filepath


# ============================================================
# SHOW SUMMARY
# ============================================================

def show_summary(df: pd.DataFrame) -> None:
    """Print data summary for dashboard insights."""
    
    print("\n" + "="*60)
    print("📊 DATA SUMMARY - Perfect for Power BI!")
    print("="*60)
    
    print("\n📈 OVERALL METRICS")
    print("-"*40)
    print(f"   Total Orders: {len(df):,}")
    print(f"   Total Revenue: ₹{df['net_amount'].sum():,.2f}")
    print(f"   Total Profit: ₹{df['profit'].sum():,.2f}")
    print(f"   Avg Order Value: ₹{df['net_amount'].mean():,.2f}")
    print(f"   Profit Margin: {(df['profit'].sum() / df['net_amount'].sum() * 100):.1f}%")
    
    print("\n👥 CUSTOMER INSIGHTS")
    print("-"*40)
    print(f"   Unique Customers: {df['customer_id'].nunique():,}")
    print(f"   Avg Orders/Customer: {len(df) / df['customer_id'].nunique():.1f}")
    print(f"\n   By Segment:")
    for segment in df['customer_segment'].unique():
        count = len(df[df['customer_segment'] == segment])
        revenue = df[df['customer_segment'] == segment]['net_amount'].sum()
        print(f"      {segment}: {count} orders (₹{revenue:,.0f})")
    
    print("\n📦 PRODUCT INSIGHTS")
    print("-"*40)
    print(f"   Unique Products: {df['product'].nunique()}")
    print(f"\n   Top 5 Products by Revenue:")
    top_products = df.groupby('product')['net_amount'].sum().sort_values(ascending=False).head()
    for product, revenue in top_products.items():
        print(f"      {product}: ₹{revenue:,.0f}")
    
    print(f"\n   By Category:")
    for category in df['category'].unique():
        revenue = df[df['category'] == category]['net_amount'].sum()
        print(f"      {category}: ₹{revenue:,.0f}")
    
    print("\n🌍 REGIONAL INSIGHTS")
    print("-"*40)
    for region in df['region'].unique():
        orders = len(df[df['region'] == region])
        revenue = df[df['region'] == region]['net_amount'].sum()
        print(f"   {region}: {orders} orders (₹{revenue:,.0f})")
    
    print("\n📅 TIME INSIGHTS")
    print("-"*40)
    df['month'] = pd.to_datetime(df['order_date']).dt.to_period('M')
    monthly = df.groupby('month')['net_amount'].sum()
    print(f"   Date Range: {df['order_date'].min()} to {df['order_date'].max()}")
    print(f"   Best Month: {monthly.idxmax()} (₹{monthly.max():,.0f})")
    print(f"   Worst Month: {monthly.idxmin()} (₹{monthly.min():,.0f})")
    
    print("\n💳 PAYMENT INSIGHTS")
    print("-"*40)
    for method in df['payment_method'].unique():
        count = len(df[df['payment_method'] == method])
        pct = count / len(df) * 100
        print(f"   {method}: {count} orders ({pct:.1f}%)")
    
    print("\n📋 ORDER STATUS")
    print("-"*40)
    for status in df['order_status'].unique():
        count = len(df[df['order_status'] == status])
        pct = count / len(df) * 100
        print(f"   {status}: {count} orders ({pct:.1f}%)")


# ============================================================
# MAIN
# ============================================================

def main():
    """Generate all data files."""
    
    print("\n" + "="*60)
    print("🏭 COMPREHENSIVE SALES DATA GENERATOR")
    print("="*60)
    print(f"   Generating {NUMBER_OF_ORDERS} orders for Power BI dashboards!")
    print("="*60)
    
    # Generate main sales data
    sales_df = generate_sales_data(NUMBER_OF_ORDERS)
    
    # Generate master data
    products_df = generate_products_master()
    customers_df = generate_customers_master(sales_df)
    
    # Save all files
    print("\n📁 Saving data files...")
    
    # Main sales data
    path1 = save_data(sales_df, 'sales_data.csv')
    print(f"   ✅ {path1}")
    
    # Products master
    path2 = save_data(products_df, 'products_master.csv')
    print(f"   ✅ {path2}")
    
    # Customers master
    path3 = save_data(customers_df, 'customers_master.csv')
    print(f"   ✅ {path3}")
    
    # Also save to project root for easy access
    sales_df.to_csv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sales_data.csv'), index=False)
    print(f"   ✅ sales_data.csv (in project root)")
    
    # Show summary
    show_summary(sales_df)
    
    # Dashboard ideas
    print("\n" + "="*60)
    print("💡 POWER BI DASHBOARD IDEAS")
    print("="*60)
    print("""
    📊 KPI CARDS:
       - Total Revenue
       - Total Orders
       - Average Order Value
       - Profit Margin %
    
    📈 LINE CHARTS:
       - Monthly Revenue Trend
       - Monthly Orders Trend
       - YoY Comparison
    
    📊 BAR CHARTS:
       - Revenue by Category
       - Revenue by Region
       - Top 10 Products
       - Revenue by Payment Method
    
    🥧 PIE/DONUT CHARTS:
       - Orders by Customer Segment
       - Orders by Order Status
       - Orders by Region
    
    🗺️ MAP:
       - Revenue by City (use Bing Maps)
    
    📋 TABLES:
       - Top Customers by Revenue
       - Product Performance
       - Monthly Summary
    
    🎛️ FILTERS:
       - Date Range Slicer
       - Category Slicer
       - Region Slicer
       - Segment Slicer
    """)
    
    print("\n" + "="*60)
    print("🎉 DATA GENERATION COMPLETE!")
    print("="*60)
    print(f"\nTotal files created: 4")
    print(f"Total orders: {NUMBER_OF_ORDERS:,}")
    print(f"\nNext steps:")
    print("   1. Run ETL: python src/pipeline.py")
    print("   2. Open Power BI and connect to MySQL")
    print("   3. Or open Power BI and load sales_data.csv directly")
    print("="*60)


if __name__ == "__main__":
    main()
