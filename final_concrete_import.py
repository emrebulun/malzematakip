"""Final concrete import - skip duplicates"""

import pandas as pd
from supabase import create_client
import time

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b"

client = create_client(URL, KEY)

print("="*60)
print("FINAL CONCRETE IMPORT")
print("="*60)

# Map classes
CLASS_MAPPING = {
    'GRO BETON': 'C25',
    'C20BRUT': 'C20',
    'C16BRUT': 'C16',
    'C25BRUT': 'C25',
    'C30BRUT': 'C30',
    'C35BRUT': 'C35',
}

# Get existing waybills to skip duplicates
print("\nGetting existing waybills...")
response = client.table('concrete_logs').select('waybill_no,supplier').execute()
existing = set()
if response.data:
    for r in response.data:
        existing.add((r['waybill_no'], r['supplier']))
print(f"Found {len(existing)} existing records")

# Read Excel
print("\nReading Excel...")
df = pd.read_excel(r"C:\Users\emreb\Desktop\BETON-997.xlsx", sheet_name='Sayfa1', header=0)

df_valid = df[df['TARİH'].notna() & df['İRSALİYE NO'].notna()].copy()
df_valid['MİKTAR'] = pd.to_numeric(df_valid['MİKTAR'], errors='coerce')
df_valid = df_valid[df_valid['MİKTAR'] > 0]

print(f"Valid rows in Excel: {len(df_valid)}")

# Prepare data
batch_data = []
skipped_duplicate = 0
skipped_class = 0

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
        
        # Skip if already exists
        if (irsaliye, firma) in existing:
            skipped_duplicate += 1
            continue
        
        beton_sinifi = str(row.get('BETON SINIFI', 'C25')).strip().upper()
        if beton_sinifi == 'NAN' or not beton_sinifi:
            beton_sinifi = 'C25'
        
        beton_sinifi = CLASS_MAPPING.get(beton_sinifi, beton_sinifi)
        
        valid_classes = ['C16', 'C20', 'C25', 'C30', 'C35', 'C40', 'C45', 'C50']
        if beton_sinifi not in valid_classes:
            skipped_class += 1
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
        
    except:
        pass

print(f"\nTo import: {len(batch_data)} records")
print(f"Skipped (duplicate): {skipped_duplicate}")
print(f"Skipped (invalid class): {skipped_class}")

total_m3 = sum(r['quantity_m3'] for r in batch_data)
print(f"Total new quantity: {total_m3:,.2f} m³")

# Insert
print("\nInserting...")
batch_size = 250
inserted = 0

for i in range(0, len(batch_data), batch_size):
    batch = batch_data[i:i+batch_size]
    try:
        response = client.table('concrete_logs').insert(batch).execute()
        inserted += len(batch)
        print(f"  {inserted}/{len(batch_data)}")
        time.sleep(0.3)
    except Exception as e:
        print(f"  Error: {str(e)[:80]}")

print(f"\n{'='*60}")
print("COMPLETE")
print("="*60)
print(f"New records inserted: {inserted:,}")

# Final verify
response = client.table('concrete_logs').select('quantity_m3').execute()
if response.data:
    df_check = pd.DataFrame(response.data)
    total = df_check['quantity_m3'].sum()
    print(f"\nTotal in database:")
    print(f"  Records: {len(df_check):,}")
    print(f"  Total m³: {total:,.2f}")
    print(f"  Target: 54,124.80 m³")
    
    if abs(total - 54124.80) < 200:
        print(f"  ✓ SUCCESS!")
    else:
        print(f"  Difference: {abs(total - 54124.80):,.2f} m³")





