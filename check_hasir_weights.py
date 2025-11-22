"""Check Hasir weight columns"""

import pandas as pd

df = pd.read_excel(r"C:\Users\emreb\Desktop\Hasır_997.xlsx")

print("="*60)
print("HASIR EXCEL STRUCTURE")
print("="*60)

print(f"Total rows: {len(df)}")
print(f"\nColumns:")
for i, col in enumerate(df.columns):
    print(f"  {i}: {col}")

# Filter valid rows (with date AND waybill)
df_valid = df[df['TARİH'].notna() & df['İRSALİYE NO'].notna()]
print(f"\n\nValid rows (with date AND waybill): {len(df_valid)}")

# Check weight columns
print("\n" + "="*60)
print("WEIGHT COLUMNS ANALYSIS")
print("="*60)

weight_cols = ['İRSALİYE AĞIRLIĞI', 'AĞIRLIK', 'HASIR AĞIRLIĞI']

for col in weight_cols:
    if col in df_valid.columns:
        total = df_valid[col].sum()
        non_null = df_valid[col].notna().sum()
        print(f"\n{col}:")
        print(f"  Total: {total:,.1f} kg")
        print(f"  Non-null values: {non_null}")
    else:
        print(f"\n{col}: NOT FOUND")

# Show first 15 rows with all relevant columns
print("\n" + "="*60)
print("FIRST 15 ROWS - KEY COLUMNS")
print("="*60)

display_cols = ['TARİH', 'İRSALİYE NO', 'ADET', 'İRSALİYE AĞIRLIĞI', 'AĞIRLIK']
print(df_valid[display_cols].head(15).to_string())

# Check what we imported
print("\n\n" + "="*60)
print("WHAT WE IMPORTED TO SUPABASE")
print("="*60)

from supabase import create_client

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b"

client = create_client(URL, KEY)
response = client.table('mesh_logs').select('*').execute()

if response.data:
    df_supabase = pd.DataFrame(response.data)
    print(f"Records in Supabase: {len(df_supabase)}")
    print(f"Total weight_kg in Supabase: {df_supabase['weight_kg'].sum():,.1f} kg")
    print(f"\nFirst 10 records from Supabase:")
    print(df_supabase[['waybill_no', 'piece_count', 'weight_kg']].head(10).to_string())

print("\n" + "="*60)
print("TARGET VALUES (from user)")
print("="*60)
print("İrsaliye Ağırlığı should be: 1,750,520 kg")
print("Ağırlık (real) should be: 1,689,860 kg")


