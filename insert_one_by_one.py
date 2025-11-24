"""Insert one by one to bypass constraint"""

import pandas as pd
from supabase import create_client
import time

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b"

client = create_client(URL, KEY)

print("INSERTING ONE BY ONE (SLOW BUT WORKS)")
print("="*60)

# Read CSV
df = pd.read_csv("concrete_import.csv")
records = df.to_dict('records')

# Get current
response = client.table('concrete_logs').select('id').execute()
current = len(response.data) if response.data else 0
print(f"Current: {current}/{len(records)}")

if current >= len(records):
    print("All done!")
    exit()

# Insert one by one
inserted = 0
skipped = 0

print(f"\nInserting {len(records) - current} records...")
print("(This will take 10-15 minutes)")

for i, record in enumerate(records):
    if i < current:
        continue  # Skip already inserted
    
    try:
        response = client.table('concrete_logs').insert([record]).execute()
        if response.data:
            inserted += 1
            if inserted % 50 == 0:
                total = current + inserted
                progress = (total / len(records)) * 100
                print(f"  {total}/{len(records)} ({progress:.1f}%)")
        time.sleep(0.1)  # Small delay
        
    except Exception as e:
        skipped += 1
        if 'duplicate' not in str(e).lower():
            if skipped <= 5:
                print(f"  Error {i}: {str(e)[:50]}")

print(f"\nDone! Inserted: {inserted}, Skipped: {skipped}")

# Verify
response = client.table('concrete_logs').select('quantity_m3').execute()
df_check = pd.DataFrame(response.data)
print(f"\nTotal: {len(df_check)} records, {df_check['quantity_m3'].sum():.2f} m3")





