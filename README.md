# Sales-Data-ETL-Pipeline

This repository contains a beginner-friendly, production-minded ETL pipeline that extracts sales data from CSV files, applies cleaning and transformations with Python (pandas), and loads the result into a MySQL data warehouse designed with a star schema. Dashboards were previously generated using Python but have been removed — connect Power BI directly to the MySQL `sales_dwh` database for reporting.

## Quick overview
- Extract: read CSV(s) from `data/raw/`
- Transform: clean data, generate dimensions and fact table
- Load: write to MySQL (`sales_dwh`)

## Highlights
- Modular code in `src/` (extract, transform, load, pipeline)
- Star schema SQL in `sql/` (date, product, customer, fact_sales)
- Data generation utility: `src/generate_sample_data.py`
- Data quality checks in `src/data_quality.py`

## Tech stack
- Python 3.x
- pandas, numpy
- mysql-connector-python
- MySQL (recommended for Power BI connectivity)

## Install dependencies
Install required Python packages:

```powershell
pip install -r requirements.txt
```

## Run the ETL pipeline
1. Create the database and tables in MySQL Workbench:
	- Run `sql/01_create_database.sql`
	- Run `sql/02_create_tables.sql`
2. Copy `.env.example` → `.env` and set your DB credentials
3. Run the pipeline:

```powershell
python src/pipeline.py
```

## Connect Power BI (recommended)
You can connect Power BI Desktop directly to the MySQL server for live reports.

1. In Power BI Desktop: Get Data → MySQL database
2. Enter server and database (`sales_dwh`) and credentials
3. Use `sql/03_useful_queries.sql` as a starting point for building measures and views

Optional: If you prefer file-based sources, export CSVs from the ETL into `data/processed/` and import them into Power BI.

## Notes
- Python dashboard files were removed to avoid duplication — Power BI is recommended for the final reporting layer.
- If you want CSV exports created automatically after the ETL run, reply "add exports" and I'll add that step to `pipeline.py`.

---
Generated: 2026-03-16
