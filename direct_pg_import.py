"""Direct PostgreSQL import - much faster!"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# Supabase connection (URL-encoded password)
DB_URL = "postgresql://postgres:05344274465%2EEb@db.xmlnpyrgxlvyzphzqeug.supabase.co:5432/postgres"

CLASS_MAPPING = {
    'GRO BETON': 'C25',
    'C20BRUT': 'C20',
    'C16BRUT': 'C16',
    'C25BRUT': 'C25',
    'C30BRUT': 'C30',
    'C35BRUT': 'C35',
}

print("="*60)
print("DIRECT POSTGRESQL IMPORT")
print("="*60)

# Read CSV
print("\nReading CSV...")
df = pd.read_csv("concrete_import.csv")
print(f"Loaded {len(df)} records from CSV")
print(f"Total: {df['quantity_m3'].sum():,.2f} m³")

# Connect to PostgreSQL
print("\nConnecting to PostgreSQL...")
conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()
print("Connected!")

# Clear existing data
print("\nClearing existing concrete data...")
cursor.execute("DELETE FROM concrete_logs")
conn.commit()
print("Cleared!")

# Prepare values for bulk insert
print("\nPreparing bulk insert...")
values = []
for _, row in df.iterrows():
    values.append((
        row['date'],
        row['supplier'],
        row['waybill_no'],
        row['concrete_class'],
        row['delivery_method'],
        float(row['quantity_m3']),
        row['location_block'],
        row['notes'] if pd.notna(row['notes']) else None
    ))

print(f"Prepared {len(values)} records")

# Bulk insert
print("\nInserting all records (this is FAST)...")
insert_query = """
    INSERT INTO concrete_logs 
    (date, supplier, waybill_no, concrete_class, delivery_method, quantity_m3, location_block, notes)
    VALUES %s
"""

execute_values(cursor, insert_query, values, page_size=1000)
conn.commit()

print("Done!")

# Verify
cursor.execute("SELECT COUNT(*), SUM(quantity_m3) FROM concrete_logs")
count, total = cursor.fetchone()

print(f"\n{'='*60}")
print("COMPLETE")
print("="*60)
print(f"Records in database: {count:,}")
print(f"Total m³: {total:,.2f}")
print(f"Expected: 54,124.80 m³")

if abs(total - 54124.80) < 200:
    print("\nSUCCESS!")
else:
    print(f"\nDifference: {abs(total - 54124.80):,.2f} m³")

cursor.close()
conn.close()

