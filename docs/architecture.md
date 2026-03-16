# 🏗️ Architecture Documentation

## Overview

This document explains the architecture of the Sales Data ETL Pipeline in detail.

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                               DATA FLOW OVERVIEW                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌──────────────────────────────────────────────────────────────────────────────┐   │
│  │                             1. EXTRACT LAYER                                  │   │
│  │  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                     │   │
│  │  │ sales_jan   │     │ sales_feb   │     │ sales_mar   │   ...CSV files     │   │
│  │  │ .csv        │     │ .csv        │     │ .csv        │                     │   │
│  │  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘                     │   │
│  │         │                   │                   │                             │   │
│  │         └───────────────────┼───────────────────┘                             │   │
│  │                             │                                                 │   │
│  │                             ▼                                                 │   │
│  │                    ┌─────────────────┐                                        │   │
│  │                    │  pandas.read_csv │  extract.py                          │   │
│  │                    └────────┬────────┘                                        │   │
│  └─────────────────────────────┼────────────────────────────────────────────────┘   │
│                                │                                                     │
│                                ▼                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────┐   │
│  │                            2. TRANSFORM LAYER                                 │   │
│  │                                                                               │   │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐ │   │
│  │  │                          transform.py                                    │ │   │
│  │  │                                                                          │ │   │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │   │
│  │  │  │ Handle       │  │ Convert      │  │ Standardize  │  │ Calculate    │ │ │   │
│  │  │  │ Missing      │─▶│ Data Types   │─▶│ Text         │─▶│ Metrics      │ │ │   │
│  │  │  │ Values       │  │              │  │              │  │              │ │ │   │
│  │  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │ │   │
│  │  │                                                                          │ │   │
│  │  │  ┌──────────────────────────────────────────────────────────────────┐   │ │   │
│  │  │  │                    DATA QUALITY VALIDATION                        │   │ │   │
│  │  │  │  ✓ No duplicates  ✓ No negatives  ✓ Valid dates  ✓ No nulls      │   │ │   │
│  │  │  └──────────────────────────────────────────────────────────────────┘   │ │   │
│  │  └─────────────────────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────────────┘   │
│                                │                                                     │
│                                ▼                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────┐   │
│  │                              3. LOAD LAYER                                    │   │
│  │                                                                               │   │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐ │   │
│  │  │                              MySQL Database                              │ │   │
│  │  │                                                                          │ │   │
│  │  │  ┌─────────────────┐                                                     │ │   │
│  │  │  │ staging_sales   │◀─────────  Raw data lands here first               │ │   │
│  │  │  └────────┬────────┘                                                     │ │   │
│  │  │           │                                                              │ │   │
│  │  │           ▼                                                              │ │   │
│  │  │  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐    │ │   │
│  │  │  │   dim_product   │     │   dim_customer  │     │    dim_date     │    │ │   │
│  │  │  │  ─────────────  │     │  ─────────────  │     │  ─────────────  │    │ │   │
│  │  │  │  product_id     │     │  customer_id    │     │  date_id        │    │ │   │
│  │  │  │  product_name   │     │  customer_name  │     │  full_date      │    │ │   │
│  │  │  │  category       │     │  segment        │     │  month, year    │    │ │   │
│  │  │  │  unit_price     │     │  city           │     │  quarter        │    │ │   │
│  │  │  └────────┬────────┘     └────────┬────────┘     └────────┬────────┘    │ │   │
│  │  │           │                       │                       │             │ │   │
│  │  │           └───────────────────────┼───────────────────────┘             │ │   │
│  │  │                                   │                                      │ │   │
│  │  │                                   ▼                                      │ │   │
│  │  │                        ┌─────────────────────┐                          │ │   │
│  │  │                        │     fact_sales      │                          │ │   │
│  │  │                        │  ─────────────────  │                          │ │   │
│  │  │                        │  sales_id           │                          │ │   │
│  │  │                        │  order_id           │                          │ │   │
│  │  │                        │  date_id  ──────────┼─▶ FK to dim_date        │ │   │
│  │  │                        │  product_id ────────┼─▶ FK to dim_product     │ │   │
│  │  │                        │  customer_id ───────┼─▶ FK to dim_customer    │ │   │
│  │  │                        │  quantity           │                          │ │   │
│  │  │                        │  unit_price         │                          │ │   │
│  │  │                        │  total_amount       │                          │ │   │
│  │  │                        └─────────────────────┘                          │ │   │
│  │  │                                                                          │ │   │
│  │  └─────────────────────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────────────┘   │
│                                │                                                     │
│                                ▼                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────┐   │
│  │                           4. PRESENTATION LAYER                               │   │
│  │                                                                               │   │
│  │  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐         │   │
│  │  │   Power BI      │     │  MySQL Queries  │     │    Reports      │         │   │
│  │  │   Dashboards    │     │  & Views        │     │    & Exports    │         │   │
│  │  └─────────────────┘     └─────────────────┘     └─────────────────┘         │   │
│  └──────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Database Schema Details

### Why Star Schema?

**Star Schema** is the most common data warehouse design because:

1. **Simple to understand** - Easy to visualize
2. **Fast queries** - Fewer JOINs needed
3. **Works with BI tools** - Power BI, Tableau love star schemas
4. **Flexible analysis** - Slice and dice by any dimension

### Table Relationships

```
                         ┌─────────────┐
                         │ dim_product │
                         │ ─────────── │
                         │ PK: product_id
                         └──────▲──────┘
                                │
                                │ FK: product_id
                                │
┌─────────────┐          ┌─────┴───────┐          ┌─────────────┐
│dim_customer │          │ fact_sales  │          │  dim_date   │
│ ─────────── │          │ ─────────── │          │ ─────────── │
│ PK: customer_id◄───────│ FK: customer_id       │ PK: date_id │
└─────────────┘          │ FK: date_id ──────────▶└─────────────┘
                         │ FK: product_id        │
                         │                        │
                         │ order_id              │
                         │ quantity              │
                         │ total_amount          │
                         └────────────────────────┘

PK = Primary Key (unique identifier)
FK = Foreign Key (links to another table)
```

---

## ETL Process Details

### 1. Extract Phase

**Purpose**: Get data from source systems

**Input**: CSV files in `data/raw/` folder

**Output**: pandas DataFrame with raw data

**Code**: `src/extract.py`

```python
# What happens:
1. Find all CSV files in the raw data folder
2. Read each file using pandas.read_csv()
3. Add metadata columns (_source_file, _loaded_at)
4. Combine all files into one DataFrame
```

### 2. Transform Phase

**Purpose**: Clean and prepare data for analysis

**Input**: Raw DataFrame from Extract

**Output**: Cleaned DataFrame + Dimension data

**Code**: `src/transform.py`

```python
# What happens:
1. Handle missing values (drop or fill)
2. Convert data types (strings to numbers, dates)
3. Standardize text (trim whitespace, fix capitalization)
4. Calculate new columns (total_amount = price × quantity)
5. Validate data quality (no negatives, no duplicates)
6. Prepare dimension data (unique products, customers)
```

### 3. Load Phase

**Purpose**: Save data to MySQL database

**Input**: Cleaned DataFrame + Dimension data

**Output**: Data in database tables

**Code**: `src/load.py`

```python
# What happens:
1. Connect to MySQL database
2. Load raw data to staging_sales (for audit trail)
3. Load unique products to dim_product (UPSERT)
4. Load unique customers to dim_customer (UPSERT)
5. Load sales transactions to fact_sales
6. Close connection
```

### 4. Quality Check Phase

**Purpose**: Verify data integrity

**Code**: `src/data_quality.py`

```python
# What happens:
1. Check row counts in all tables
2. Verify no orphan records (all FKs have matches)
3. Check for duplicate orders
4. Check for negative values
5. Generate quality report
```

---

## Key Design Decisions

### 1. Why Staging Table?

- **Audit trail**: Keep record of raw data
- **Debugging**: Easy to compare raw vs. transformed
- **Recovery**: Can re-transform if needed
- **Validation**: Check data before loading to final tables

### 2. Why Separate Dimensions?

- **No data duplication**: Customer name stored once
- **Easy updates**: Change product price in one place
- **Historical tracking**: Can add SCD (Slowly Changing Dimensions)
- **Better performance**: Smaller fact table

### 3. Why Date Dimension?

Instead of storing just the date, we pre-calculate:
- Day of week (Monday, Tuesday...)
- Month name (January, February...)
- Quarter (Q1, Q2, Q3, Q4)
- Is weekend? (True/False)

**Benefits**:
- Faster queries (no date functions needed)
- Consistent date handling
- Easy to add holidays, fiscal periods

---

## Performance Considerations

### Indexes

We create indexes on frequently queried columns:

```sql
-- Fact table indexes
INDEX idx_date (date_id)      -- For time-based queries
INDEX idx_product (product_id) -- For product analysis
INDEX idx_customer (customer_id) -- For customer analysis
```

### Batch Loading

Instead of inserting one row at a time:

```python
# Slow (one insert per row)
for row in data:
    cursor.execute("INSERT INTO ...", row)

# Fast (batch insert)
cursor.executemany("INSERT INTO ...", data)
```

---

## Future Improvements

When you're ready to level up:

1. **Add Airflow** - Schedule the pipeline to run automatically
2. **Add dbt** - Transform data using SQL in a managed way
3. **Add more data sources** - APIs, other databases
4. **Add SCD Type 2** - Track historical changes in dimensions
5. **Add incremental loads** - Only process new data
6. **Add more quality checks** - Data profiling, anomaly detection
