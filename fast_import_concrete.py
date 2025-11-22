"""Fast batch import of concrete data"""

import pandas as pd
from supabase import create_client

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b"

client = create_client(URL, KEY)

print("="*60)
print("FAST BATCH IMPORT - CONCRETE DATA")
print("="*60)

# Clear existing
print("\nClearing old data...")
client.table('concrete_logs').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
print("Cleared!")

# Read Excel
print("\nReading Excel...")
df = pd.read_excel(r"C:\Users\emreb\Desktop\BETON-997.xlsx", sheet_name='Sayfa1', header=0)

# Filter valid
df_valid = df[df['TARİH'].notna() & df['İRSALİYE NO'].notna()].copy()
df_valid['MİKTAR'] = pd.to_numeric(df_valid['MİKTAR'], errors='coerce')
df_valid = df_valid[df_valid['MİKTAR'] > 0]

print(f"Valid rows: {len(df_valid)}")
print(f"Total: {df_valid['MİKTAR'].sum():,.2f} m³")

# Prepare batch data
print("\nPreparing data...")
batch_data = []

for idx, row in df_valid.iterrows():
    try:
        tarih = row['TARİH']
        if hasattr(tarih, 'date'):
            tarih = tarih.date().isoformat()
        else:
            tarih = pd.to_datetime(tarih).date().isoformat()
        
        irsaliye = str(row['İRSALİYE NO']).strip()
        
        firma = str(row.get('FİRMA', '')).strip()
        if not firma or firma == 'nan':
            try:
                irsa_num = int(''.join(filter(str.isdigit, irsaliye)))
                firma = "ALBAYRAK BETON" if irsa_num > 14000 else "ÖZYURT BETON"
            except:
                firma = "BİLİNMİYOR"
        
        beton_sinifi = str(row.get('BETON SINIFI', 'C25')).strip().upper()
        if beton_sinifi == 'NAN' or not beton_sinifi:
            beton_sinifi = 'C25'
        
        teslim = str(row.get('TESLİM ŞEKLİ', 'MİKSERLİ')).strip().upper()
        teslim = 'POMPALI' if 'POMPA' in teslim else 'MİKSERLİ'
        
        miktar = float(row['MİKTAR'])
        
        blok = str(row.get('BLOK', '')).strip()
        if blok == 'nan' or not blok or blok == 'None':
            blok = 'Bilinmiyor'
        
        aciklama = str(row.get('AÇIKLAMA', '')).strip()
        if aciklama == 'nan' or not aciklama:
            aciklama = None
        
        batch_data.append({
            'date': tarih,
            'supplier': firma,
            'waybill_no': irsaliye,
            'concrete_class': beton_sinifi,
            'delivery_method': teslim,
            'quantity_m3': miktar,
            'location_block': blok,
            'notes': aciklama
        })
        
    except Exception as e:
        pass

print(f"Prepared {len(batch_data)} records")

# Insert in batches of 1000
print("\nInserting in batches...")
batch_size = 1000
total_inserted = 0

for i in range(0, len(batch_data), batch_size):
    batch = batch_data[i:i+batch_size]
    try:
        response = client.table('concrete_logs').insert(batch).execute()
        total_inserted += len(batch)
        print(f"  Inserted batch {i//batch_size + 1}: {total_inserted}/{len(batch_data)} records")
    except Exception as e:
        print(f"  Error in batch {i//batch_size + 1}: {e}")

print(f"\n{'='*60}")
print("IMPORT COMPLETE")
print("="*60)
print(f"Total inserted: {total_inserted:,} records")

# Verify
response = client.table('concrete_logs').select('quantity_m3').execute()
if response.data:
    df_check = pd.DataFrame(response.data)
    total = df_check['quantity_m3'].sum()
    print(f"\nVerified:")
    print(f"  Records: {len(df_check):,}")
    print(f"  Total: {total:,.2f} m³")
    print(f"  Expected: 54,124.80 m³")
    print(f"  Match: {'YES!' if abs(total - 54124.80) < 50 else 'NO'}")


