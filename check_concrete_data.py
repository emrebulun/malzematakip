"""Check concrete data in Supabase"""

from supabase import create_client
import pandas as pd

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b"

client = create_client(URL, KEY)

print("="*60)
print("CONCRETE DATA IN SUPABASE")
print("="*60)

response = client.table('concrete_logs').select('*').execute()

if response.data:
    df = pd.DataFrame(response.data)
    print(f"Total records: {len(df)}")
    print(f"Total quantity_m3: {df['quantity_m3'].sum():.1f} m³")
    
    print(f"\nFirst 10 records:")
    print(df[['date', 'supplier', 'waybill_no', 'concrete_class', 'quantity_m3']].head(10))
    
    print(f"\nAll quantities:")
    print(df['quantity_m3'].tolist())
else:
    print("No concrete data found!")





