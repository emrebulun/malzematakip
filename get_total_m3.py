"""Get total m3 from all records"""

from supabase import create_client
import pandas as pd

client = create_client(
    'https://xmlnpyrgxlvyzphzqeug.supabase.co',
    'sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b'
)

print("Getting ALL concrete records...")

all_data = []
page_size = 1000
page = 0

while True:
    response = client.table('concrete_logs').select('quantity_m3').range(page * page_size, (page + 1) * page_size - 1).execute()
    if not response.data or len(response.data) == 0:
        break
    all_data.extend(response.data)
    print(f"  Page {page + 1}: {len(response.data)} records")
    page += 1

print(f"\nTotal records: {len(all_data)}")

df = pd.DataFrame(all_data)
total_m3 = df['quantity_m3'].sum()

print(f"Total m3: {total_m3:,.2f}")
print(f"Expected: 54,124.80 m3")

diff = abs(total_m3 - 54124.80)
if diff < 200:
    print(f"\nSUCCESS! (difference: {diff:.2f})")
else:
    print(f"\nDifference: {diff:,.2f} m3")


