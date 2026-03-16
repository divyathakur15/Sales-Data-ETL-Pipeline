# Project structure and Power BI workflow

This document describes the finalized project layout and where to place Power BI artifacts.

Repository root (key files/folders):

- `src/` - ETL source code
  - `config.py`        - DB and environment configuration
  - `extract.py`       - Extract functions
  - `transform.py`     - Data cleaning and dimension preparation
  - `load.py`          - Database load utilities
  - `pipeline.py`      - Main ETL orchestrator (run this)
  - `data_quality.py`  - Quality checks
  - `generate_sample_data.py` - Synthetic data generator

- `data/`
  - `raw/`             - Raw CSV input files (source of truth)
  - `processed/`       - Processed outputs (summary files, exports)

- `sql/`
  - `01_create_database.sql` - Create database
  - `02_create_tables.sql`   - Create tables (star schema)
  - `03_useful_queries.sql`  - Helpful queries for reporting

- `docs/`               - Architecture and guides
- `PROJECT_GUIDE.md`    - Quick project guide and run instructions
- `SETUP_GUIDE.md`      - Setup steps (MySQL, .env)

What was removed
----------------
All Python dashboard scripts and generated dashboard image files were removed to focus on Power BI for reporting.

Power BI workflow recommendation
------------------------------
1. Connect Power BI Desktop to the `sales_dwh` MySQL database.
2. If preferred, export CSVs from the ETL into `data/processed/` and import them into Power BI.
3. Create a `powerbi/` folder at repo root and store `.pbix` files there.

Export suggestion (optional):
- `data/processed/fact_sales_export.csv`
- `data/processed/dim_product.csv`
- `data/processed/dim_customer.csv`
- `data/processed/dim_date.csv`

Next steps
----------
- Reply "yes" if you want CSV exports added to the pipeline.

---
Generated on: 2026-03-16
