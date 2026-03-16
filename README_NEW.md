# 🛒 Sales Data ETL Pipeline

A **beginner-friendly, professional-grade ETL pipeline** that demonstrates data engineering best practices. This project extracts sales data from CSV files, transforms it using Python, and loads it into a MySQL data warehouse using a star schema design.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [How It Works](#-how-it-works)
- [Power BI Integration](#-power-bi-integration)
- [Data Model](#-data-model)
- [Skills Demonstrated](#-skills-demonstrated)

---

## 🎯 Overview

This project demonstrates a complete **ETL (Extract, Transform, Load)** pipeline:

| Step | Description | Technology |
|------|-------------|------------|
| **Extract** | Read data from CSV files | Python (pandas) |
| **Transform** | Clean, validate, enrich data | Python (pandas) |
| **Load** | Save to dimensional data warehouse | MySQL |
| **Visualize** | Create dashboards | Power BI |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ETL PIPELINE ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   📁 DATA SOURCES          🔄 ETL PROCESS           🗄️ DATA WAREHOUSE       │
│   ───────────────          ─────────────           ────────────────         │
│                                                                              │
│   ┌───────────┐     ┌─────────────────────────┐    ┌─────────────────┐     │
│   │           │     │                         │    │                 │     │
│   │  CSV      │────▶│  EXTRACT                │───▶│  staging_sales  │     │
│   │  Files    │     │  (Read files)           │    │  (Raw data)     │     │
│   │           │     │                         │    │                 │     │
│   └───────────┘     │  TRANSFORM              │    ├─────────────────┤     │
│                     │  • Clean data           │    │                 │     │
│                     │  • Validate quality     │    │  dim_product    │     │
│                     │  • Calculate metrics    │    │  dim_customer   │     │
│                     │                         │    │  dim_date       │     │
│                     │  LOAD                   │    │                 │     │
│                     │  • Load dimensions      │───▶│  fact_sales     │     │
│                     │  • Load facts           │    │  (Star Schema)  │     │
│                     │  • Quality checks       │    │                 │     │
│                     │                         │    └────────┬────────┘     │
│                     └─────────────────────────┘             │              │
│                                                              │              │
│                                                              ▼              │
│                                                    ┌─────────────────┐     │
│                                                    │   📊 Power BI    │     │
│                                                    │   Dashboards    │     │
│                                                    └─────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

- ✅ **Modular Code Structure** - Separate files for Extract, Transform, Load
- ✅ **Star Schema Design** - Fact and dimension tables for analytics
- ✅ **Data Validation** - Quality checks at every step
- ✅ **Error Handling** - Graceful error messages with troubleshooting tips
- ✅ **Configuration Management** - Environment variables for security
- ✅ **Detailed Logging** - Track what the pipeline does
- ✅ **Idempotent Loads** - Safe to run multiple times
- ✅ **Well Documented** - Extensive comments explaining every step

---

## 📁 Project Structure

```
Sales-Data-ETL-Pipeline/
│
├── 📄 README.md                    # This file
├── 📄 PROJECT_GUIDE.md             # Detailed learning guide
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # Environment variables template
├── 📄 .gitignore                   # Files to ignore in Git
│
├── 📂 data/                        # Data files
│   ├── 📂 raw/                     # Input CSV files
│   ├── 📂 processed/               # Cleaned output files
│   └── 📂 sample/                  # Sample test data
│
├── 📂 sql/                         # SQL scripts
│   ├── 📄 01_create_database.sql   # Create database
│   ├── 📄 02_create_tables.sql     # Create all tables
│   └── 📄 03_useful_queries.sql    # Analytics queries
│
├── 📂 src/                         # Python source code
│   ├── 📄 config.py                # Configuration settings
│   ├── 📄 extract.py               # EXTRACT: Read data
│   ├── 📄 transform.py             # TRANSFORM: Clean data
│   ├── 📄 load.py                  # LOAD: Save to database
│   ├── 📄 data_quality.py          # Quality checks
│   └── 📄 pipeline.py              # Main ETL script
│
└── 📂 docs/                        # Documentation
    └── 📄 architecture.md          # Architecture details
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher
- MySQL Workbench (optional, but recommended)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/Sales-Data-ETL-Pipeline.git
cd Sales-Data-ETL-Pipeline

# Install Python dependencies
pip install -r requirements.txt

# Create your environment file
copy .env.example .env
# Edit .env and add your MySQL password
```

### Step 2: Setup Database

Open MySQL Workbench and run these scripts in order:

1. `sql/01_create_database.sql` - Creates the database
2. `sql/02_create_tables.sql` - Creates all tables

### Step 3: Run the Pipeline

```bash
python src/pipeline.py
```

### Step 4: View Results

```bash
# Run analytics queries
# Open sql/03_useful_queries.sql in MySQL Workbench
```

---

## 🔄 How It Works

### Step 1: Extract
```python
# Read CSV file
df = pd.read_csv('sales_data.csv')
```

### Step 2: Transform
```python
# Clean data
df['total_amount'] = df['price'] * df['quantity']
df['date'] = pd.to_datetime(df['date'])

# Validate
assert df['price'].min() >= 0, "Negative prices found!"
```

### Step 3: Load
```python
# Load to dimension tables (Products, Customers)
# Load to fact table (Sales transactions)
INSERT INTO fact_sales (...) VALUES (...)
```

### Step 4: Quality Check
```sql
-- Check for orphan records
SELECT COUNT(*) FROM fact_sales f
LEFT JOIN dim_product p ON f.product_id = p.product_id
WHERE p.product_id IS NULL;  -- Should be 0
```

---

## 📊 Power BI Integration

### Connect Power BI to MySQL

1. Open Power BI Desktop
2. Click **Get Data** → **MySQL database**
3. Enter connection details:
   - Server: `localhost`
   - Database: `sales_dwh`
4. Select tables or use the `vw_sales_summary` view
5. Create your visualizations!

### Suggested Visualizations

- 📈 **Line Chart**: Sales trend over time
- 📊 **Bar Chart**: Revenue by product
- 🥧 **Pie Chart**: Sales by customer segment
- 📋 **Table**: Top 10 orders
- 🎯 **KPI Cards**: Total Revenue, Order Count, AOV

---

## 🗄️ Data Model

### Star Schema

```
                    ┌─────────────┐
                    │ dim_product │
                    └──────┬──────┘
                           │
┌─────────────┐    ┌──────┴──────┐    ┌─────────────┐
│ dim_customer│────│ fact_sales  │────│  dim_date   │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Tables

| Table | Type | Description |
|-------|------|-------------|
| `staging_sales` | Staging | Raw data landing zone |
| `dim_date` | Dimension | Calendar attributes |
| `dim_product` | Dimension | Product details |
| `dim_customer` | Dimension | Customer details |
| `fact_sales` | Fact | Sales transactions |

---

## 🎓 Skills Demonstrated

| Category | Skills |
|----------|--------|
| **Programming** | Python, SQL, pandas |
| **Data Engineering** | ETL, Data Pipelines, Data Modeling |
| **Database** | MySQL, Star Schema, Dimensional Modeling |
| **Data Quality** | Validation, Testing, Error Handling |
| **Best Practices** | Modular Code, Documentation, Version Control |
| **Tools** | Git, MySQL Workbench, Power BI |

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)

---

## 🙏 Acknowledgments

- Built as a learning project for data engineering
- Inspired by real-world ETL pipelines
- Thanks to the open-source community

---

⭐ **Star this repo if you found it helpful!**
