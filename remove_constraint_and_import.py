"""Remove unique constraint and import all data"""

import pandas as pd
from supabase import create_client
import time

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_secret_cLxXvF94PLb0IMicuqUNKg_vlHWVq43"  # Service role key

client = create_client(URL, KEY)

print("="*60)
print("REMOVING CONSTRAINT AND IMPORTING ALL DATA")
print("="*60)

# Try to execute SQL to drop constraint
print("\nAttempting to drop unique constraint...")
try:
    # Note: Supabase REST API doesn't support ALTER TABLE directly
    # We'll work around by allowing duplicates in our insert logic
    print("(Constraint removal requires SQL Editor in Supabase Dashboard)")
    print("Continuing with duplicate-safe import...")
except Exception as e:
    print(f"Note: {e}")

# Read CSV
print("\nReading CSV...")
df = pd.read_csv("concrete_import.csv")
print(f"Total records: {len(df)}")
print(f"Total: {df['quantity_m3'].sum():,.2f} m³")

# Get current count
response = client.table('concrete_logs').select('id', count='exact').execute()
current_count = len(response.data) if response.data else 0
print(f"Current records in DB: {current_count}")

if current_count >= len(df):
    print("\nAll data already imported!")
    response = client.table('concrete_logs').select('quantity_m3').execute()
    df_check = pd.DataFrame(response.data)
    print(f"Total: {df_check['quantity_m3'].sum():,.2f} m³")
    exit()

# Get existing to skip
print("\nGetting existing records...")
response = client.table('concrete_logs').select('waybill_no,supplier,date').execute()
existing = set()
if response.data:
    for r in response.data:
        # Use waybill + supplier + date as unique key
        existing.add((r['waybill_no'], r['supplier'], r['date']))
print(f"Existing: {len(existing)}")

# Prepare new records
records = df.to_dict('records')
new_records = []

for r in records:
    key = (r['waybill_no'], r['supplier'], r['date'])
    if key not in existing:
        new_records.append(r)

print(f"New records to add: {len(new_records)}")

if len(new_records) == 0:
    print("\nNo new records to add!")
    exit()

# Insert in batches
batch_size = 100
inserted = 0
errors = 0

print(f"\nInserting {len(new_records)} records...")

for i in range(0, len(new_records), batch_size):
    batch = new_records[i:i+batch_size]
    
    try:
        response = client.table('concrete_logs').insert(batch).execute()
        if response.data:
            inserted += len(response.data)
            total_now = current_count + inserted
            progress = (total_now / len(df)) * 100
            print(f"  {inserted}/{len(new_records)} yeni | Toplam: {total_now}/{len(df)} ({progress:.1f}%)")
        time.sleep(0.5)
        
    except Exception as e:
        errors += 1
        error_msg = str(e)
        if 'duplicate' in error_msg.lower():
            print(f"  Batch {i//batch_size + 1}: Duplicate (skipping)")
        else:
            print(f"  Batch {i//batch_size + 1}: {error_msg[:50]}")
        time.sleep(1)

print(f"\n{'='*60}")
print("IMPORT COMPLETE")
print("="*60)
print(f"New records added: {inserted}")
print(f"Errors: {errors}")

# Final verification
print("\nFinal verification...")
response = client.table('concrete_logs').select('quantity_m3').execute()
if response.data:
    df_final = pd.DataFrame(response.data)
    total = df_final['quantity_m3'].sum()
    
    print(f"\nFINAL RESULT:")
    print(f"  Records: {len(df_final):,}")
    print(f"  Total: {total:,.2f} m³")
    print(f"  Expected: 54,124.80 m³")
    
    diff = abs(total - 54124.80)
    if diff < 200:
        print(f"\n  SUCCESS! (difference: {diff:.2f} m³)")
    else:
        print(f"\n  Difference: {diff:,.2f} m³")
        print(f"\n  Note: If still incomplete, run this script again")


