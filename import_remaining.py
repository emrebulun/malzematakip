"""Import remaining records with NaN handling"""

import pandas as pd
from supabase import create_client
import time
import math

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b"

client = create_client(URL, KEY)

print("Importing remaining records...")

# Get existing waybills
response = client.table('concrete_logs').select('waybill_no,supplier').execute()
existing = set()
if response.data:
    for r in response.data:
        existing.add((r['waybill_no'], r['supplier']))

print(f"Existing: {len(existing)}")

# Read CSV
df = pd.read_csv("concrete_import.csv")
records = df.to_dict('records')

# Find missing
missing = []
for r in records:
    if (r['waybill_no'], r['supplier']) not in existing:
        # Clean NaN values
        cleaned = {}
        for key, value in r.items():
            if pd.isna(value) or (isinstance(value, float) and math.isnan(value)):
                if key == 'notes':
                    cleaned[key] = None
                elif key == 'location_block':
                    cleaned[key] = 'Bilinmiyor'
                else:
                    cleaned[key] = None
            else:
                cleaned[key] = value
        missing.append(cleaned)

print(f"Missing: {len(missing)}")

if len(missing) == 0:
    print("All records imported!")
else:
    # Import one by one for NaN records
    print("\nImporting missing records...")
    inserted = 0
    
    for i, record in enumerate(missing):
        try:
            response = client.table('concrete_logs').insert([record]).execute()
            if response.data:
                inserted += 1
                if inserted % 50 == 0:
                    print(f"  {inserted}/{len(missing)}")
            time.sleep(0.1)
        except Exception as e:
            if i < 5:
                print(f"  Error: {str(e)[:60]}")
    
    print(f"\nInserted: {inserted}/{len(missing)}")

# Final check
all_data = []
page = 0
while page < 20:
    response = client.table('concrete_logs').select('quantity_m3').range(page * 1000, (page + 1) * 1000 - 1).execute()
    if not response.data:
        break
    all_data.extend(response.data)
    page += 1

df_final = pd.DataFrame(all_data)
total = df_final['quantity_m3'].sum()

print(f"\nFINAL:")
print(f"  Records: {len(df_final):,}")
print(f"  Total: {total:,.2f} m3")
print(f"  Expected: 54,124.80 m3")

if abs(total - 54124.80) < 300:
    print("\n  SUCCESS!")





