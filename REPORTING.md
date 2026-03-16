# Reporting & Power BI Connection

This project uses Power BI for final reporting. Use the instructions below to connect and model your data.

Power BI (Live connection to MySQL)
----------------------------------
1. Open Power BI Desktop → Get Data → MySQL database
2. Enter Server and Database: `sales_dwh` and provide credentials
3. Select the tables: `dim_date`, `dim_product`, `dim_customer`, `fact_sales` or run custom SQL from `sql/03_useful_queries.sql`
4. Create relationships on keys: `date_id`, `product_id`, `customer_id`
5. Build measures (SUM, COUNT, AVERAGE) and visuals (KPI cards, line charts, bar charts, maps)

Optional: CSV Export Workflow
----------------------------
If you prefer file-based imports for Power BI, the pipeline can export CSVs into `data/processed/`.
Suggested files to export:

- `data/processed/fact_sales_export.csv`
- `data/processed/dim_product.csv`
- `data/processed/dim_customer.csv`
- `data/processed/dim_date.csv`

If you want exports added to the ETL pipeline, reply `add exports` and I'll implement it in `src/pipeline.py`.
