"""Find actual data rows in Excel files"""

import pandas as pd

# Check BETON file for sheets and actual data
print("="*60)
print("BETON FILE - CHECKING SHEETS")
print("="*60)

beton_file = r"C:\Users\emreb\Desktop\BETON-997.xlsx"
xl_file = pd.ExcelFile(beton_file)
print(f"Sheet names: {xl_file.sheet_names}")

for sheet in xl_file.sheet_names:
    print(f"\n--- Sheet: {sheet} ---")
    df = pd.read_excel(beton_file, sheet_name=sheet, nrows=10)
    print(f"Shape: {df.shape}")
    print(df.head())

# Check DEMIR file 
print("\n\n" + "="*60)
print("DEMIR FILE - First 15 rows")
print("="*60)

demir_file = r"C:\Users\emreb\Desktop\Demir_997.xlsx"
df_demir = pd.read_excel(demir_file, header=1, nrows=15)
print(df_demir)

# Check HASIR file
print("\n\n" + "="*60)
print("HASIR FILE - First 15 rows")
print("="*60)

hasir_file = r"C:\Users\emreb\Desktop\Hasır_997.xlsx"
df_hasir = pd.read_excel(hasir_file, header=0, nrows=15)
print(df_hasir[['TARİH', 'FİRMA', 'İRSALİYE NO', 'ADET', 'AĞIRLIK']])





