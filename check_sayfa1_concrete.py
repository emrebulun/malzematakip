"""Check Sayfa1 sheet for concrete data"""

import pandas as pd

file_path = r"C:\Users\emreb\Desktop\BETON-997.xlsx"

print("="*60)
print("SAYFA1 SHEET ANALYSIS")
print("="*60)

# Read with header at row 0
df = pd.read_excel(file_path, sheet_name='Sayfa1', header=0)

print(f"Total rows: {len(df)}")
print(f"Columns: {list(df.columns)}")

# Check MİKTAR column
if 'MİKTAR' in df.columns:
    df['MİKTAR'] = pd.to_numeric(df['MİKTAR'], errors='coerce')
    
    print(f"\nMİKTAR analysis:")
    print(f"  Non-null values: {df['MİKTAR'].notna().sum()}")
    print(f"  Total: {df['MİKTAR'].sum():,.2f} m³")
    
    # Filter valid rows (with date and waybill)
    df_valid = df[df['TARİH'].notna() & df['İRSALİYE NO'].notna()]
    print(f"\nValid rows (with date & waybill): {len(df_valid)}")
    print(f"Total MİKTAR (valid rows): {df_valid['MİKTAR'].sum():,.2f} m³")
    
    print(f"\nFirst 10 valid rows:")
    print(df_valid[['TARİH', 'İRSALİYE NO', 'BETON SINIFI', 'MİKTAR', 'BLOK']].head(10))
    
    print(f"\nLast 10 valid rows:")
    print(df_valid[['TARİH', 'İRSALİYE NO', 'BETON SINIFI', 'MİKTAR', 'BLOK']].tail(10))
    
    # Check if this is the data we need
    if abs(df_valid['MİKTAR'].sum() - 54124.80) < 100:
        print(f"\n✅ THIS IS THE CORRECT SHEET!")
        print(f"   Total matches expected: {df_valid['MİKTAR'].sum():,.2f} m³")
    else:
        print(f"\n⚠️ Total doesn't match expected (54,124.80 m³)")
        print(f"   Difference: {abs(df_valid['MİKTAR'].sum() - 54124.80):,.2f} m³")
else:
    print("\n❌ MİKTAR column not found!")





