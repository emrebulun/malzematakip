"""Slow but steady import with small batches"""

import pandas as pd
from supabase import create_client
import time

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b"

client = create_client(URL, KEY)

print("="*60)
print("IMPORTING WITH SMALL BATCHES")
print("="*60)

# Read CSV
df = pd.read_csv("concrete_import.csv")
print(f"\nTotal records: {len(df)}")
print(f"Total m³: {df['quantity_m3'].sum():,.2f}")

# Convert to list of dicts
records = df.to_dict('records')

# Get existing count
response = client.table('concrete_logs').select('id', count='exact').execute()
existing_count = response.count if hasattr(response, 'count') else 0
print(f"Existing records: {existing_count}")

# Insert in VERY small batches with delays
batch_size = 50  # Small batches
inserted = 0
errors = 0

print(f"\nInserting in batches of {batch_size}...")
print("This will take a few minutes but will work!")

for i in range(0, len(records), batch_size):
    batch = records[i:i+batch_size]
    
    try:
        response = client.table('concrete_logs').insert(batch).execute()
        if response.data:
            inserted += len(response.data)
            print(f"  {inserted}/{len(records)} ({(inserted/len(records)*100):.1f}%)")
        time.sleep(1)  # 1 second delay between batches
        
    except Exception as e:
        errors += 1
        error_msg = str(e)
        if 'duplicate' in error_msg.lower():
            print(f"  Batch {i//batch_size + 1}: Skipped (duplicates)")
        else:
            print(f"  Batch {i//batch_size + 1}: Error - {error_msg[:60]}")
        time.sleep(2)  # Longer delay after error

print(f"\n{'='*60}")
print("COMPLETE")
print("="*60)
print(f"Inserted: {inserted}/{len(records)}")
print(f"Errors: {errors}")

# Final verify
response = client.table('concrete_logs').select('quantity_m3').execute()
if response.data:
    df_check = pd.DataFrame(response.data)
    total = df_check['quantity_m3'].sum()
    print(f"\nFinal total:")
    print(f"  Records: {len(df_check):,}")
    print(f"  Total m³: {total:,.2f}")
    print(f"  Target: 54,124.80 m³")



