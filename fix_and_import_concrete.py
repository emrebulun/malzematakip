"""Fix concrete class mapping and import"""

import pandas as pd
from supabase import create_client
import time

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b"

client = create_client(URL, KEY)

print("="*60)
print("CONCRETE IMPORT WITH CLASS MAPPING")
print("="*60)

# Map non-standard classes to standard ones
CLASS_MAPPING = {
    'GRO BETON': 'C25',
    'C20BRUT': 'C20',
    'C16BRUT': 'C16',
    'C25BRUT': 'C25',
    'C30BRUT': 'C30',
    'C35BRUT': 'C35',
}

# Clear all existing data
print("\nClearing ALL existing concrete data...")
try:
    # Delete in smaller batches to avoid timeout
    deleted_total = 0
    while True:
        response = client.table('concrete_logs').delete().limit(1000).neq('id', '00000000-0000-0000-0000-000000000000').execute()
        if not response.data or len(response.data) == 0:
            break
        deleted_total += len(response.data)
        print(f"  Deleted {deleted_total} records...")
        time.sleep(0.1)
    print(f"Cleared {deleted_total} records!")
except Exception as e:
    print(f"Clear error: {e}")

# Read Excel
print("\nReading Excel...")
df = pd.read_excel(r"C:\Users\emreb\Desktop\BETON-997.xlsx", sheet_name='Sayfa1', header=0)

# Filter
df_valid = df[df['TARİH'].notna() & df['İRSALİYE NO'].notna()].copy()
df_valid['MİKTAR'] = pd.to_numeric(df_valid['MİKTAR'], errors='coerce')
df_valid = df_valid[df_valid['MİKTAR'] > 0]

print(f"Valid rows: {len(df_valid)}")

# Prepare data
batch_data = []
skipped = 0

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
        
        # Map concrete class
        beton_sinifi = str(row.get('BETON SINIFI', 'C25')).strip().upper()
        if beton_sinifi == 'NAN' or not beton_sinifi:
            beton_sinifi = 'C25'
        
        # Apply mapping
        beton_sinifi = CLASS_MAPPING.get(beton_sinifi, beton_sinifi)
        
        # Skip if not in valid enum
        valid_classes = ['C16', 'C20', 'C25', 'C30', 'C35', 'C40', 'C45', 'C50']
        if beton_sinifi not in valid_classes:
            skipped += 1
            continue
        
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
        skipped += 1

print(f"Prepared {len(batch_data)} records (skipped {skipped})")

# Calculate total
total_m3 = sum(r['quantity_m3'] for r in batch_data)
print(f"Total quantity: {total_m3:,.2f} m³")

# Insert in batches
print("\nInserting batches (500 per batch)...")
batch_size = 500
inserted = 0

for i in range(0, len(batch_data), batch_size):
    batch = batch_data[i:i+batch_size]
    try:
        response = client.table('concrete_logs').insert(batch).execute()
        inserted += len(batch)
        print(f"  Batch {i//batch_size + 1}: {inserted}/{len(batch_data)}")
        time.sleep(0.2)  # Small delay between batches
    except Exception as e:
        print(f"  Error batch {i//batch_size + 1}: {str(e)[:100]}")

print(f"\n{'='*60}")
print("COMPLETE")
print("="*60)
print(f"Inserted: {inserted:,} / {len(batch_data):,}")

# Verify
response = client.table('concrete_logs').select('quantity_m3').execute()
if response.data:
    df_check = pd.DataFrame(response.data)
    total = df_check['quantity_m3'].sum()
    print(f"\nFinal verification:")
    print(f"  Records in database: {len(df_check):,}")
    print(f"  Total m³: {total:,.2f}")
    print(f"  Expected: 54,124.80 m³")
    
    diff = abs(total - 54124.80)
    if diff < 100:
        print(f"  SUCCESS! (difference: {diff:.2f})")
    else:
        print(f"  Difference: {diff:,.2f} m³")



