# 🚀 Supabase Integration Guide

## Overview
Complete guide to integrate Supabase (PostgreSQL) cloud database with your Construction Material Tracking System.

## 📁 Files Created

1. **`supabase_schema.sql`** - PostgreSQL database schema
2. **`db_manager.py`** - Database connection and operations manager
3. **`.streamlit/secrets.toml`** - Supabase credentials (DO NOT COMMIT)
4. **`supabase_integration_example.py`** - Complete integration example
5. **`.gitignore`** - Updated to exclude secrets
6. **`SUPABASE_INTEGRATION_README.md`** - This file

## 🎯 Quick Start

### Step 1: Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up / Log in
3. Click "New Project"
4. Fill in:
   - **Name**: Construction Material Tracking
   - **Database Password**: Choose a strong password (save it!)
   - **Region**: Choose closest to you
5. Wait for project to be created (~2 minutes)

### Step 2: Run SQL Schema

1. In Supabase Dashboard, go to **SQL Editor**
2. Click "New Query"
3. Copy entire contents of `supabase_schema.sql`
4. Paste into editor
5. Click "Run" (or press Ctrl+Enter)
6. Verify: You should see "Success" messages
7. Check tables: Go to **Table Editor** - you should see:
   - `concrete_logs`
   - `rebar_logs`
   - `mesh_logs`

### Step 3: Get Connection String

1. In Supabase Dashboard, go to **Settings** > **Database**
2. Scroll to "Connection string" section
3. Select **URI** tab
4. Copy the connection string (looks like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.abcdefghijklmn.supabase.co:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with your actual database password

### Step 4: Configure Secrets

1. Open `.streamlit/secrets.toml`
2. Replace the placeholder connection string with your actual one:
   ```toml
   [supabase]
   connection_string = "postgresql://postgres:YourActualPassword@db.yourprojectref.supabase.co:5432/postgres"
   ```
3. Save the file
4. **IMPORTANT**: Never commit this file to Git!

### Step 5: Install Dependencies

```bash
pip install sqlalchemy psycopg2-binary streamlit pandas
```

### Step 6: Test Connection

Run the example app:
```bash
streamlit run supabase_integration_example.py
```

You should see:
- 🟢 "Connected to Supabase" in sidebar
- Empty dashboard (no data yet)
- Forms to add data

### Step 7: Add Test Data

1. Go to "Concrete" page
2. Fill in the form
3. Click "Save Record"
4. ✅ You should see success message
5. Data appears in table below
6. Go to "Dashboard" - see the metrics update!

## 📊 Database Schema

### Tables

#### 1. concrete_logs
```sql
- id (UUID, Primary Key)
- date (Date)
- supplier (Text)
- waybill_no (Text)
- concrete_class (Enum: C16, C20, C25, C30, C35, C40, GRO, ŞAP)
- delivery_method (Enum: POMPALI, MİKSERLİ)
- quantity_m3 (Float)
- location_block (Text)
- notes (Text)
- created_at (Timestamp)
- updated_at (Timestamp)
```

#### 2. rebar_logs
```sql
- id (UUID, Primary Key)
- date (Date)
- supplier (Text)
- waybill_no (Text)
- project_stage (Text)
- manufacturer (Text)
- q8_kg, q10_kg, q12_kg, q14_kg, q16_kg (Float)
- q18_kg, q20_kg, q22_kg, q25_kg, q28_kg, q32_kg (Float)
- total_weight_kg (Float)
- notes (Text)
- created_at (Timestamp)
- updated_at (Timestamp)
```

#### 3. mesh_logs
```sql
- id (UUID, Primary Key)
- date (Date)
- supplier (Text)
- waybill_no (Text)
- mesh_type (Enum: Q, R, TR)
- dimensions (Text)
- piece_count (Integer)
- weight_kg (Float)
- usage_location (Text)
- notes (Text)
- created_at (Timestamp)
- updated_at (Timestamp)
```

### Features
- ✅ UUID primary keys
- ✅ Automatic timestamps
- ✅ Unique constraints (prevent duplicate waybills)
- ✅ Check constraints (positive values)
- ✅ Indexes for performance
- ✅ Views for analytics
- ✅ Triggers for auto-update

## 🔧 Using db_manager.py

### Initialize Connection

```python
from db_manager import get_db_manager

# Get cached database manager
db = get_db_manager()

# Test connection
if db.test_connection():
    st.success("Connected!")
```

### Concrete Operations

```python
# Add concrete
concrete_data = {
    'date': datetime.now().date(),
    'supplier': 'ÖZYURT BETON',
    'waybill_no': '12345',
    'concrete_class': 'C30',
    'delivery_method': 'POMPALI',
    'quantity_m3': 15.5,
    'location_block': 'GK1',
    'notes': 'Test delivery'
}
success = db.add_concrete(concrete_data)

# Get all concrete logs
df = db.get_concrete_logs()

# Get filtered logs
df = db.get_concrete_logs(
    start_date='2024-01-01',
    end_date='2024-12-31',
    supplier='ÖZYURT BETON'
)

# Get summary
summary = db.get_concrete_summary()
# Returns: {
#   'total_deliveries': 10,
#   'total_quantity_m3': 150.5,
#   'supplier_count': 2,
#   'location_count': 5
# }

# Get by supplier
df = db.get_concrete_by_supplier()

# Get by location
df = db.get_concrete_by_location()
```

### Rebar Operations

```python
# Add rebar
rebar_data = {
    'date': datetime.now().date(),
    'supplier': 'ŞAHİN DEMİR',
    'waybill_no': 'D-001',
    'project_stage': '3.ETAP',
    'manufacturer': 'Kardemir',
    'q8_kg': 500,
    'q10_kg': 750,
    'q12_kg': 1000,
    'q14_kg': 0,
    # ... other diameters
    'total_weight_kg': 2250  # or auto-calculated
}
success = db.add_rebar(rebar_data)

# Get all rebar logs
df = db.get_rebar_logs()

# Get summary
summary = db.get_rebar_summary()
# Returns totals for each diameter + overall total

# Get by diameter
df = db.get_rebar_by_diameter()
# Returns: DataFrame with columns [diameter, total_kg]
```

### Mesh Operations

```python
# Add mesh
mesh_data = {
    'date': datetime.now().date(),
    'supplier': 'DOFER',
    'waybill_no': 'M-001',
    'mesh_type': 'Q',
    'dimensions': '215x500',
    'piece_count': 50,
    'weight_kg': 1250.5,
    'usage_location': 'GK1'
}
success = db.add_mesh(mesh_data)

# Get all mesh logs
df = db.get_mesh_logs()

# Get summary
summary = db.get_mesh_summary()

# Get by type
df = db.get_mesh_by_type()
```

## 📝 Integration into Existing App

### Option 1: Replace Local Storage

In your existing `app.py`:

```python
# OLD (local storage)
if 'beton_df' not in st.session_state:
    st.session_state.beton_df = pd.DataFrame()

# NEW (Supabase)
from db_manager import get_db_manager
db = get_db_manager()
beton_df = db.get_concrete_logs()
```

### Option 2: Hybrid Mode

Keep local storage as fallback:

```python
from db_manager import get_db_manager

try:
    db = get_db_manager()
    if db.test_connection():
        st.session_state.use_supabase = True
        st.sidebar.success("🟢 Supabase Connected")
    else:
        st.session_state.use_supabase = False
        st.sidebar.warning("🟡 Using Local Mode")
except:
    st.session_state.use_supabase = False
    st.sidebar.warning("🟡 Using Local Mode")

# In your forms
if submitted:
    if st.session_state.use_supabase:
        # Save to Supabase
        db.add_concrete(data)
    else:
        # Save to session state
        st.session_state.beton_df = pd.concat([...])
```

### Option 3: Complete Migration

Use `supabase_integration_example.py` as your new `app.py`:

```bash
# Backup old app
mv app.py app_old.py

# Use new Supabase-integrated app
cp supabase_integration_example.py app.py

# Run
streamlit run app.py
```

## 🔐 Security Best Practices

### 1. Protect Secrets
```bash
# Add to .gitignore
echo ".streamlit/secrets.toml" >> .gitignore

# Verify it's not tracked
git status
```

### 2. Use Environment Variables (Production)

Instead of `secrets.toml`, use environment variables:

```python
import os
from sqlalchemy import create_engine

connection_string = os.getenv('SUPABASE_CONNECTION_STRING')
engine = create_engine(connection_string)
```

Set in your hosting platform:
```bash
# Heroku
heroku config:set SUPABASE_CONNECTION_STRING="postgresql://..."

# Streamlit Cloud
# Add in Settings > Secrets
```

### 3. Enable Row Level Security (RLS)

In Supabase SQL Editor:

```sql
-- Enable RLS
ALTER TABLE concrete_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE rebar_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE mesh_logs ENABLE ROW LEVEL SECURITY;

-- Create policy (example - adjust based on your needs)
CREATE POLICY "Allow all for authenticated users"
ON concrete_logs
FOR ALL
USING (auth.role() = 'authenticated');
```

### 4. Use Read-Only Keys

For dashboards/reporting, create a read-only database user:

```sql
-- Create read-only role
CREATE ROLE readonly;
GRANT CONNECT ON DATABASE postgres TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;

-- Create read-only user
CREATE USER dashboard_viewer WITH PASSWORD 'secure_password';
GRANT readonly TO dashboard_viewer;
```

## 📈 Performance Optimization

### 1. Use Indexes (Already Created)

The schema includes indexes on:
- Date columns (for time-based queries)
- Supplier columns (for filtering)
- Location columns (for grouping)

### 2. Use Views for Complex Queries

Pre-created views:
- `v_concrete_by_supplier`
- `v_concrete_by_location`
- `v_rebar_by_diameter`
- `v_mesh_by_type`

Query views instead of base tables:
```python
query = "SELECT * FROM v_concrete_by_supplier"
df = db._execute_query(query)
```

### 3. Implement Caching

```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_concrete_logs():
    db = get_db_manager()
    return db.get_concrete_logs()

# Use cached version
df = get_cached_concrete_logs()
```

### 4. Pagination for Large Datasets

```python
def get_concrete_logs_paginated(page=1, page_size=100):
    offset = (page - 1) * page_size
    query = f"""
    SELECT * FROM concrete_logs
    ORDER BY date DESC
    LIMIT {page_size} OFFSET {offset}
    """
    return db._execute_query(query)
```

## 🧪 Testing

### Test Connection
```python
from db_manager import get_db_manager

db = get_db_manager()
assert db.test_connection() == True
print("✅ Connection successful")
```

### Test CRUD Operations
```python
# Test concrete
data = {
    'date': '2024-11-21',
    'supplier': 'TEST SUPPLIER',
    'waybill_no': 'TEST-001',
    'concrete_class': 'C30',
    'delivery_method': 'POMPALI',
    'quantity_m3': 10.0
}

# Create
assert db.add_concrete(data) == True
print("✅ Create successful")

# Read
df = db.get_concrete_logs()
assert len(df) > 0
print("✅ Read successful")

# Verify
assert 'TEST-001' in df['waybill_no'].values
print("✅ Data verified")
```

## 🐛 Troubleshooting

### Problem: "Failed to connect to Supabase"

**Solutions:**
1. Check `secrets.toml` has correct connection string
2. Verify password is correct (no special characters causing issues)
3. Check project is not paused (Supabase free tier pauses after inactivity)
4. Test connection string in a PostgreSQL client (pgAdmin, DBeaver)

### Problem: "relation does not exist"

**Solutions:**
1. Make sure you ran `supabase_schema.sql` in SQL Editor
2. Check you're connected to correct database
3. Verify tables exist: Go to Table Editor in Supabase

### Problem: "duplicate key value violates unique constraint"

**Solutions:**
1. You're trying to insert duplicate waybill number for same supplier
2. Change waybill number or supplier
3. Or remove unique constraint if not needed

### Problem: "value too long for type"

**Solutions:**
1. Check your input data length
2. Increase column size in schema if needed:
   ```sql
   ALTER TABLE concrete_logs 
   ALTER COLUMN notes TYPE TEXT;
   ```

### Problem: "permission denied"

**Solutions:**
1. Check RLS policies if enabled
2. Verify user has correct permissions
3. Disable RLS for testing:
   ```sql
   ALTER TABLE concrete_logs DISABLE ROW LEVEL SECURITY;
   ```

## 📚 Additional Resources

### Supabase Documentation
- [Supabase Docs](https://supabase.com/docs)
- [PostgreSQL Tutorial](https://www.postgresql.org/docs/current/tutorial.html)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)

### Streamlit Resources
- [Streamlit SQL Connection](https://docs.streamlit.io/library/api-reference/connections/st.connection)
- [Streamlit Secrets](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)

### Example Queries

```sql
-- Total concrete by month
SELECT 
    DATE_TRUNC('month', date) as month,
    SUM(quantity_m3) as total_m3
FROM concrete_logs
GROUP BY month
ORDER BY month DESC;

-- Top suppliers
SELECT 
    supplier,
    COUNT(*) as deliveries,
    SUM(quantity_m3) as total_m3
FROM concrete_logs
GROUP BY supplier
ORDER BY total_m3 DESC;

-- Rebar usage by diameter
SELECT 
    SUM(q8_kg) as q8_total,
    SUM(q10_kg) as q10_total,
    SUM(q12_kg) as q12_total
FROM rebar_logs;
```

## 🎉 Success Checklist

- [ ] Supabase project created
- [ ] SQL schema executed successfully
- [ ] Tables visible in Table Editor
- [ ] Connection string copied
- [ ] `secrets.toml` configured
- [ ] Dependencies installed
- [ ] Test app runs without errors
- [ ] Can add concrete record
- [ ] Can add rebar record
- [ ] Can add mesh record
- [ ] Data persists after refresh
- [ ] Dashboard shows correct metrics
- [ ] `.gitignore` updated
- [ ] Secrets NOT committed to Git

## 🚀 Next Steps

1. **Migrate Existing Data**
   - Export from Excel
   - Import to Supabase using forms or bulk insert

2. **Add Authentication**
   - Enable Supabase Auth
   - Add login page
   - Implement RLS policies

3. **Deploy to Cloud**
   - Deploy to Streamlit Cloud
   - Add secrets in Streamlit Cloud settings
   - Test production deployment

4. **Add Advanced Features**
   - Real-time updates
   - Email notifications
   - PDF report generation
   - Mobile app

---

**Version**: 1.0.0  
**Database**: Supabase (PostgreSQL)  
**Status**: ✅ Ready for Production  
**Last Updated**: November 21, 2024





