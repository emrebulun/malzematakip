"""Check AĞIRLIK column details"""

import pandas as pd

df = pd.read_excel(r"C:\Users\emreb\Desktop\Hasır_997.xlsx")
df_valid = df[df['TARİH'].notna() & df['İRSALİYE NO'].notna()]

print("="*60)
print("AĞIRLIK COLUMN ANALYSIS")
print("="*60)

print(f"\nTotal valid rows (with date & waybill): {len(df_valid)}")

# AĞIRLIK analysis
agirlik_not_null = df_valid[df_valid['AĞIRLIK'].notna()]
print(f"\nAĞIRLIK (non-null only):")
print(f"  Count: {len(agirlik_not_null)}")
print(f"  Sum: {agirlik_not_null['AĞIRLIK'].sum():,.1f} kg")

# İRSALİYE AĞIRLIĞI analysis
irs_not_null = df_valid[df_valid['İRSALİYE AĞIRLIĞI'].notna()]
print(f"\nİRSALİYE AĞIRLIĞI (non-null only):")
print(f"  Count: {len(irs_not_null)}")
print(f"  Sum: {irs_not_null['İRSALİYE AĞIRLIĞI'].sum():,.1f} kg")

print(f"\n{'='*60}")
print("USER EXPECTATIONS")
print("="*60)
print(f"İrsaliye Ağırlığı should be: 1,750,520 kg")
print(f"Gerçek Ağırlık (AĞIRLIK) should be: 1,689,860 kg")

print(f"\n{'='*60}")
print("ANALYSIS")
print("="*60)
print(f"Difference in AĞIRLIK: {abs(agirlik_not_null['AĞIRLIK'].sum() - 1689860):,.1f} kg")
print(f"Difference in İRSALİYE AĞIRLIĞI: {abs(irs_not_null['İRSALİYE AĞIRLIĞI'].sum() - 1750520):,.1f} kg")

# Show rows where AĞIRLIK is null but İRSALİYE AĞIRLIĞI is not
missing_agirlik = df_valid[df_valid['AĞIRLIK'].isna() & df_valid['İRSALİYE AĞIRLIĞI'].notna()]
print(f"\nRows with missing AĞIRLIK (but has İRSALİYE AĞIRLIĞI): {len(missing_agirlik)}")
if len(missing_agirlik) > 0:
    print("These rows:")
    print(missing_agirlik[['İRSALİYE NO', 'ADET', 'İRSALİYE AĞIRLIĞI']].to_string())


