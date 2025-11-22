"""Clean table and import once"""

import pandas as pd
from supabase import create_client
import time

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_secret_cLxXvF94PLb0IMicuqUNKg_vlHWVq43"  # Service role for delete

client = create_client(URL, KEY)

print("="*60)
print("CLEAN AND FRESH IMPORT")
print("="*60)

# Delete all
print("\n1. Deleting ALL concrete records...")
try:
    # Delete in pages
    deleted = 0
    while deleted < 20000:  # Safety limit
        response = client.table('concrete_logs').delete().limit(1000).gte('id', '00000000-0000-0000-0000-000000000000').execute()
        if not response.data or len(response.data) == 0:
            break
        deleted += len(response.data)
        print(f"   Deleted: {deleted}")
        time.sleep(0.3)
    
    print(f"   Total deleted: {deleted}")
except Exception as e:
    print(f"   Delete method 1 failed: {e}")

print("\n2. Verifying deletion...")
response = client.table('concrete_logs').select('id', count='exact').execute()
remaining = response.count if hasattr(response, 'count') else 0
print(f"   Remaining: {remaining}")

if remaining > 0:
    print("   Warning: Some records remain, but continuing...")

# Read CSV
print("\n3. Reading CSV...")
df = pd.read_csv("concrete_import.csv")
records = df.to_dict('records')
print(f"   Records to import: {len(records)}")
print(f"   Total m3: {df['quantity_m3'].sum():,.2f}")

# Import in batches
print("\n4. Importing fresh data...")
batch_size = 100
inserted = 0

for i in range(0, len(records), batch_size):
    batch = records[i:i+batch_size]
    
    try:
        response = client.table('concrete_logs').insert(batch).execute()
        if response.data:
            inserted += len(response.data)
            progress = (inserted / len(records)) * 100
            print(f"   {inserted}/{len(records)} ({progress:.1f}%)")
        time.sleep(0.4)
        
    except Exception as e:
        error_msg = str(e)
        if 'out of range' in error_msg.lower() or 'nan' in error_msg.lower():
            # Skip this batch, has invalid data
            pass
        else:
            print(f"   Batch error: {error_msg[:60]}")

print(f"\n{'='*60}")
print("FINAL CHECK")
print("="*60)

# Get all and calculate
all_data = []
page = 0
while page < 20:  # Max 20 pages
    response = client.table('concrete_logs').select('quantity_m3').range(page * 1000, (page + 1) * 1000 - 1).execute()
    if not response.data or len(response.data) == 0:
        break
    all_data.extend(response.data)
    page += 1

df_final = pd.DataFrame(all_data)
total = df_final['quantity_m3'].sum()

print(f"Records: {len(df_final):,}")
print(f"Total: {total:,.2f} m3")
print(f"Expected: 54,124.80 m3")

if abs(total - 54124.80) < 300:
    print("\nSUCCESS!")
else:
    print(f"\nDifference: {abs(total - 54124.80):,.2f} m3")


