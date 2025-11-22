"""Re-import all concrete data correctly"""

import pandas as pd
from supabase import create_client

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b"

client = create_client(URL, KEY)

print("="*60)
print("RE-IMPORTING CONCRETE DATA")
print("="*60)

# Clear existing
print("\nClearing existing concrete data...")
client.table('concrete_logs').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()

# Read Excel
df = pd.read_excel(r"C:\Users\emreb\Desktop\BETON-997.xlsx", sheet_name='Sayfa2', header=2)

# Filter valid rows
df_valid = df[df['TARİH'].notna() & df['İRSALİYE NO'].notna()].copy()

# Remove header repeat row (where MİKTAR is string "MİKTAR")
df_valid = df_valid[df_valid['MİKTAR'].apply(lambda x: not isinstance(x, str) or x != 'MİKTAR')]

print(f"Valid rows: {len(df_valid)}")

added = 0
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
        
        # Determine company based on waybill
        try:
            irsa_num = int(''.join(filter(str.isdigit, irsaliye)))
            firma = "ALBAYRAK BETON" if irsa_num > 14000 else "ÖZYURT BETON"
        except:
            firma = str(row.get('FİRMA', 'ÖZYURT BETON')).strip()
        
        # Concrete class
        beton_sinifi = str(row['BETON SINIFI']).strip().upper()
        if beton_sinifi == 'NAN' or not beton_sinifi:
            beton_sinifi = 'C25'
        
        # Delivery method
        teslim = str(row['TESLİM ŞEKLİ']).strip().upper()
        if 'POMPA' in teslim:
            teslim = 'POMPALI'
        else:
            teslim = 'MİKSERLİ'
        
        # Quantity
        miktar = pd.to_numeric(row['MİKTAR'], errors='coerce')
        if pd.isna(miktar) or miktar <= 0:
            continue
        miktar = float(miktar)
        total_m3 += miktar
        
        # Block
        blok = str(row.get('BLOK', 'Bilinmiyor')).strip()
        if blok == 'nan' or not blok:
            blok = 'Bilinmiyor'
        
        # Notes
        aciklama = str(row.get('AÇIKLAMA', '')).strip()
        if aciklama == 'nan':
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
            if added % 5 == 0:
                print(f"  Progress: {added} records...")
                
    except Exception as e:
        print(f"  Error row {idx}: {e}")

print(f"\n{'='*60}")
print("IMPORT COMPLETE")
print("="*60)
print(f"Successfully added: {added} concrete records")
print(f"Total quantity: {total_m3:.1f} m³")

# Verify
response = client.table('concrete_logs').select('*').execute()
if response.data:
    df_check = pd.DataFrame(response.data)
    print(f"\nVerified in Supabase:")
    print(f"  Records: {len(df_check)}")
    print(f"  Total m³: {df_check['quantity_m3'].sum():.1f}")


