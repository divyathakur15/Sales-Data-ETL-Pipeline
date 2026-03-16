# 📚 SETUP GUIDE - Read This First!

## Step-by-Step Setup Instructions

Follow these steps in order to get your ETL pipeline working.

---

## 🔧 Step 1: Install Python Packages

Open your terminal/command prompt in the project folder and run:

```powershell
pip install -r requirements.txt
```

This installs:
- `pandas` - For data manipulation
- `mysql-connector-python` - To connect to MySQL
- `python-dotenv` - For secure configuration

---

## 🔐 Step 2: Configure Database Connection

1. **Copy the example environment file:**
   ```powershell
   copy .env.example .env
   ```

2. **Edit the `.env` file** and change the password:
   ```
   DB_PASSWORD=your_actual_mysql_password
   ```

   ⚠️ **Important**: Never share or commit your `.env` file!

---

## 🗄️ Step 3: Create the Database (MySQL Workbench)

1. Open **MySQL Workbench**
2. Connect to your MySQL Server
3. Open `sql/01_create_database.sql`
4. Click the ⚡ lightning bolt to run
5. You should see: "Database sales_dwh created successfully!"

---

## 📊 Step 4: Create the Tables

1. In MySQL Workbench, open `sql/02_create_tables.sql`
2. Click the ⚡ lightning bolt to run
3. You should see multiple "table created!" messages
4. At the end, you'll see a summary of all tables

**Troubleshooting:**
- If you get an error about `sales_dwh` not existing, run Step 3 first
- If you see "Access denied", check your MySQL username/password

---

## ▶️ Step 5: Run the ETL Pipeline

In your terminal:

```powershell
cd e:\Sales_Data_ETL_Pipeline\Sales-Data-ETL-Pipeline
python src/pipeline.py
```

**Expected Output:**
```
🚀 SALES DATA ETL PIPELINE
============================
STEP 1: EXTRACT
📂 EXTRACT: Reading file...
✅ Extracted 5 rows

STEP 2: TRANSFORM
🔧 TRANSFORM: Cleaning data...
✅ Cleaned 5 rows

STEP 3: LOAD
✅ Connected to MySQL
✅ Loaded products
✅ Loaded customers
✅ Loaded fact_sales

STEP 4: QUALITY CHECKS
✅ ALL DATA QUALITY CHECKS PASSED!

✅ ETL PIPELINE COMPLETED SUCCESSFULLY!
```

---

## 📈 Step 6: Verify in MySQL Workbench

Run these queries to verify data was loaded:

```sql
USE sales_dwh;

-- Check dimension tables
SELECT * FROM dim_product;
SELECT * FROM dim_customer;

-- Check fact table
SELECT * FROM fact_sales;

-- Check the summary view
SELECT * FROM vw_sales_summary;
```

---

## 📊 Step 7: Connect Power BI (Optional)

1. Open Power BI Desktop
2. Click **Get Data** → **MySQL database**
3. Enter:
   - Server: `localhost`
   - Database: `sales_dwh`
4. Enter your MySQL credentials
5. Select `vw_sales_summary` view or individual tables
6. Create your visualizations!

---

## ❓ Common Issues & Solutions

### Issue: "mysql.connector not found"
```powershell
pip install mysql-connector-python
```

### Issue: "Access denied for user 'root'"
- Check your password in `.env` file
- Make sure MySQL is running

### Issue: "Unknown database 'sales_dwh'"
- Run `sql/01_create_database.sql` first

### Issue: "Table doesn't exist"
- Run `sql/02_create_tables.sql` first

### Issue: "No module named 'dotenv'"
```powershell
pip install python-dotenv
```

---

## 🎉 Success!

If everything worked, you now have:
- ✅ A working ETL pipeline
- ✅ A star schema data warehouse
- ✅ Sample data loaded
- ✅ Ready for Power BI visualization

**Next Steps:**
1. Add more data to `data/raw/` folder
2. Run the pipeline again
3. Create Power BI dashboards
4. Customize the code for your needs

---

## 📞 Need Help?

If you're stuck:
1. Check the error message carefully
2. Read `PROJECT_GUIDE.md` for concepts
3. Check `docs/architecture.md` for technical details
