"""Check Excel concrete data"""

import pandas as pd

df = pd.read_excel(r"C:\Users\emreb\Desktop\BETON-997.xlsx", sheet_name='Sayfa2', header=2)

print("="*60)
print("BETON EXCEL DATA")
print("="*60)

print(f"Total rows: {len(df)}")

# Filter valid
df_valid = df[df['TARİH'].notna() & df['İRSALİYE NO'].notna()]
print(f"Valid rows (with date & waybill): {len(df_valid)}")

print(f"\nFirst 10 rows:")
print(df_valid[['TARİH', 'İRSALİYE NO', 'MİKTAR', 'BLOK']].head(20))

print(f"\nMİKTAR column types:")
print(df_valid['MİKTAR'].apply(type).value_counts())

# Try to convert to numeric
df_valid['MİKTAR_NUM'] = pd.to_numeric(df_valid['MİKTAR'], errors='coerce')
print(f"\nTotal MİKTAR: {df_valid['MİKTAR_NUM'].sum():.1f} m³")

print(f"\nNon-numeric MİKTAR values:")
non_numeric = df_valid[df_valid['MİKTAR_NUM'].isna()]
if len(non_numeric) > 0:
    print(non_numeric[['TARİH', 'İRSALİYE NO', 'MİKTAR']])

