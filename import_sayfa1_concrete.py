"""Import all concrete data from Sayfa1"""

import pandas as pd
from supabase import create_client

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b"

client = create_client(URL, KEY)

print("="*60)
print("IMPORTING ALL CONCRETE DATA FROM SAYFA1")
print("="*60)

# Clear existing
print("\nClearing existing concrete data...")
client.table('concrete_logs').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
print("Cleared!")

# Read Sayfa1
df = pd.read_excel(r"C:\Users\emreb\Desktop\BETON-997.xlsx", sheet_name='Sayfa1', header=0)

print(f"\nTotal rows in Excel: {len(df)}")

# Filter valid rows
df_valid = df[df['TARİH'].notna() & df['İRSALİYE NO'].notna()].copy()
print(f"Valid rows (with date & waybill): {len(df_valid)}")

# Convert MİKTAR to numeric
df_valid['MİKTAR'] = pd.to_numeric(df_valid['MİKTAR'], errors='coerce')
print(f"Total MİKTAR: {df_valid['MİKTAR'].sum():,.2f} m³")

added = 0
errors = 0
total_m3 = 0

for idx, row in df_valid.iterrows():
    try:
        # Date
        tarih = row['TARİH']
        if hasattr(tarih, 'date'):
            tarih = tarih.date().isoformat()
        else:
            tarih = pd.to_datetime(tarih).date().isoformat()
        
        # Waybill
        irsaliye = str(row['İRSALİYE NO']).strip()
        
        # Company
        firma = str(row.get('FİRMA', '')).strip()
        if not firma or firma == 'nan':
            # Determine from waybill
            try:
                irsa_num = int(''.join(filter(str.isdigit, irsaliye)))
                firma = "ALBAYRAK BETON" if irsa_num > 14000 else "ÖZYURT BETON"
            except:
                firma = "BİLİNMİYOR"
        
        # Concrete class
        beton_sinifi = str(row.get('BETON SINIFI', 'C25')).strip().upper()
        if beton_sinifi == 'NAN' or not beton_sinifi:
            beton_sinifi = 'C25'
        
        # Delivery method
        teslim = str(row.get('TESLİM ŞEKLİ', 'MİKSERLİ')).strip().upper()
        if 'POMPA' in teslim:
            teslim = 'POMPALI'
        else:
            teslim = 'MİKSERLİ'
        
        # Quantity
        miktar = row.get('MİKTAR')
        if pd.isna(miktar) or miktar <= 0:
            continue
        miktar = float(miktar)
        total_m3 += miktar
        
        # Block
        blok = str(row.get('BLOK', '')).strip()
        if blok == 'nan' or not blok or blok == 'None':
            blok = 'Bilinmiyor'
        
        # Notes
        aciklama = str(row.get('AÇIKLAMA', '')).strip()
        if aciklama == 'nan' or not aciklama:
            aciklama = None
        
        # Prepare data
        data = {
            'date': tarih,
            'supplier': firma,
            'waybill_no': irsaliye,
            'concrete_class': beton_sinifi,
            'delivery_method': teslim,
            'quantity_m3': miktar,
            'location_block': blok,
            'notes': aciklama
        }
        
        # Insert
        response = client.table('concrete_logs').insert(data).execute()
        
        if response.data:
            added += 1
            if added % 500 == 0:
                print(f"  Progress: {added} records... ({total_m3:,.1f} m³)")
        else:
            errors += 1
            if errors <= 5:
                print(f"  Error row {idx}: No data returned")
                
    except Exception as e:
        errors += 1
        if errors <= 5:
            print(f"  Error row {idx}: {str(e)[:100]}")

print(f"\n{'='*60}")
print("IMPORT COMPLETE")
print("="*60)
print(f"Successfully added: {added:,} concrete records")
print(f"Total quantity: {total_m3:,.2f} m³")
print(f"Errors: {errors}")

# Verify
response = client.table('concrete_logs').select('*').execute()
if response.data:
    df_check = pd.DataFrame(response.data)
    supabase_total = df_check['quantity_m3'].sum()
    print(f"\nVerified in Supabase:")
    print(f"  Records: {len(df_check):,}")
    print(f"  Total m³: {supabase_total:,.2f}")
    
    if abs(supabase_total - 54124.80) < 100:
        print(f"\nSUCCESS! Total matches expected!")
    else:
        print(f"\nDifference from expected (54,124.80): {abs(supabase_total - 54124.80):,.2f} m³")





