# 🎓 Sales Data ETL Pipeline - Beginner's Guide

## 📁 Project Structure Explained

```
Sales-Data-ETL-Pipeline/
│
├── 📄 README.md                    # Project description for GitHub
├── 📄 PROJECT_GUIDE.md             # This guide - explains everything!
├── 📄 requirements.txt             # Python packages needed
├── 📄 .env.example                 # Example environment variables
│
├── 📂 data/                        # All your data files
│   ├── 📂 raw/                     # Original CSV files (input)
│   ├── 📂 processed/               # Cleaned CSV files (output)
│   └── 📂 sample/                  # Sample data for testing
│
├── 📂 sql/                         # All SQL scripts
│   ├── 📄 01_create_database.sql   # Creates the database
│   ├── 📄 02_create_tables.sql     # Creates all tables
│   └── 📄 03_useful_queries.sql    # Analytics queries for Power BI
│
├── 📂 src/                         # Python source code
│   ├── 📄 __init__.py              # Makes this a Python package
│   ├── 📄 config.py                # Configuration settings
│   ├── 📄 extract.py               # EXTRACT: Read data from files
│   ├── 📄 transform.py             # TRANSFORM: Clean and process data
│   ├── 📄 load.py                  # LOAD: Save data to MySQL
│   ├── 📄 pipeline.py              # Main ETL pipeline (runs everything)
│   └── 📄 data_quality.py          # Check data quality
│
├── 📂 tests/                       # Test your code
│   └── 📄 test_pipeline.py         # Basic tests
│
├── 📂 notebooks/                   # Jupyter notebooks for learning
│   └── 📄 01_explore_data.ipynb    # Explore your data visually
│
└── 📂 docs/                        # Documentation
    └── 📄 architecture.md          # Architecture diagram
```

---

## 🔑 Key Concepts Explained

### 1. What is ETL?

**E**xtract - **T**ransform - **L**oad

| Step | What it does | Example |
|------|--------------|---------|
| **Extract** | Get data from source | Read sales_data.csv file |
| **Transform** | Clean and improve data | Calculate total_amount, fix dates |
| **Load** | Save to destination | Insert into MySQL database |

### 2. What is a Data Warehouse?

A **Data Warehouse** is a special database designed for **analytics and reporting** (not for daily transactions).

**Key difference:**
- **OLTP** (Online Transaction Processing): Your app's database - fast writes, current data
- **OLAP** (Online Analytical Processing): Data Warehouse - fast reads, historical data

### 3. What is a Star Schema?

The most common way to organize a data warehouse:

- **Fact Table** (center): Contains numbers/measurements you want to analyze
  - Example: `fact_sales` with quantity, amount, profit
  
- **Dimension Tables** (points of the star): Contains descriptions
  - Example: `dim_customer` with customer_name, city
  - Example: `dim_product` with product_name, category
  - Example: `dim_date` with month, year, quarter

### 4. Why Separate Tables?

**Bad approach (your current single table):**
```
| order_id | customer_name | product  | price | quantity | date       |
|----------|---------------|----------|-------|----------|------------|
| ORD001   | John          | Laptop   | 50000 | 1        | 2024-01-15 |
| ORD002   | John          | Mouse    | 1500  | 2        | 2024-01-16 |  ← "John" repeated!
```

**Good approach (Star Schema):**
```
dim_customer:               fact_sales:
| id | name |               | customer_id | product_id | amount |
|----|------|               |-------------|------------|--------|
| 1  | John |               | 1           | 101        | 50000  |
                            | 1           | 102        | 3000   |
                            
Customer name stored ONCE, referenced by ID (saves space, prevents errors)
```

---

## 🚀 How to Run This Project

### Step 1: Install Requirements
```bash
pip install -r requirements.txt
```

### Step 2: Set Up MySQL
- Open MySQL Workbench
- Run `sql/01_create_database.sql`
- Run `sql/02_create_tables.sql`

### Step 3: Configure Database Connection
- Copy `.env.example` to `.env`
- Update with your MySQL password

### Step 4: Run the Pipeline
```bash
python src/pipeline.py
```

### Step 5: Check Results
- Open MySQL Workbench
- Run queries from `sql/03_useful_queries.sql`
- Connect Power BI to MySQL for visualization

---

## 📊 What You'll Learn

1. ✅ How to structure a professional Python project
2. ✅ How to design a data warehouse (Star Schema)
3. ✅ How to write clean, modular ETL code
4. ✅ How to handle errors and log activities
5. ✅ How to validate data quality
6. ✅ How to connect to databases safely
7. ✅ How to write SQL for analytics
8. ✅ How to document your project for portfolio

---

## 🎯 Skills You'll Demonstrate

| Skill | Where in Project |
|-------|------------------|
| Python | src/*.py files |
| SQL | sql/*.sql files |
| Data Modeling | Star Schema design |
| ETL Development | Extract, Transform, Load modules |
| Data Quality | data_quality.py |
| Version Control | Git commits |
| Documentation | README, comments |
