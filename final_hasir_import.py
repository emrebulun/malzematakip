"""Final Hasir import - Use ACTUAL WEIGHT (AĞIRLIK column)"""

import pandas as pd
from supabase import create_client

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b"

client = create_client(URL, KEY)

print("="*60)
print("FINAL HASIR IMPORT - USING REAL WEIGHT")
print("="*60)

# Clear existing
print("\nClearing existing mesh data...")
client.table('mesh_logs').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
print("Cleared!")

# Read Excel
df = pd.read_excel(r"C:\Users\emreb\Desktop\Hasır_997.xlsx", header=0)

# Filter: must have DATE AND WAYBILL NUMBER
df_valid = df[df['TARİH'].notna() & df['İRSALİYE NO'].notna()].copy()
print(f"\nValid rows: {len(df_valid)}")

added = 0
total_weight = 0

for idx, row in df_valid.iterrows():
    try:
        # Date
        tarih = row['TARİH']
        if hasattr(tarih, 'date'):
            tarih = tarih.date().isoformat()
        else:
            tarih = pd.to_datetime(tarih).date().isoformat()
        
        # Supplier
        firma = str(row.get('FİRMA', 'BİLİNMİYOR')).strip()
        if firma == 'nan' or not firma:
            firma = 'BİLİNMİYOR'
        
        # Waybill
        irsaliye = str(row['İRSALİYE NO']).strip()
        
        # Mesh type
        hasir_tipi = str(row.get('HASIR TİPİ', 'Q')).strip().upper()
        if hasir_tipi == 'NAN' or not hasir_tipi or hasir_tipi not in ['Q', 'R', 'TR']:
            hasir_tipi = 'Q'
        
        # Dimensions
        uzunluk = row.get('HASIR UZUNLUĞU (L)')
        en = row.get('HASIRIN ENİ(e)')
        
        if pd.notna(uzunluk) and pd.notna(en):
            olculer = f"{uzunluk}x{en}m"
        else:
            olculer = None
        
        # Piece count
        adet = row.get('ADET')
        if pd.isna(adet):
            adet = 1
        else:
            adet = int(float(adet))
            if adet <= 0:
                adet = 1
        
        # WEIGHT - Use AĞIRLIK (REAL/ACTUAL WEIGHT) column 24
        # SKIP rows where AĞIRLIK is null (user wants only real weight 1,689,860 kg)
        agirlik = row.get('AĞIRLIK')
        if pd.isna(agirlik):
            continue  # Skip this row - no real weight
        
        agirlik = float(agirlik)
        total_weight += agirlik
        
        # İRSALİYE AĞIRLIĞI for reference in notes
        irsaliye_agirlik = row.get('İRSALİYE AĞIRLIĞI')
        if pd.isna(irsaliye_agirlik):
            irsaliye_agirlik = 0
        else:
            irsaliye_agirlik = float(irsaliye_agirlik)
        
        # Usage location
        konum = row.get('SS')
        if pd.isna(konum) or str(konum).strip() == 'nan':
            konum = row.get('ETAP')
            if pd.isna(konum) or str(konum).strip() == 'nan':
                konum = None
            else:
                konum = str(konum).strip()
        else:
            konum = str(konum).strip()
        
        # Notes: show İRSALİYE AĞIRLIĞI if different from AĞIRLIK
        notes = None
        if irsaliye_agirlik > 0 and abs(irsaliye_agirlik - agirlik) > 1:
            notes = f"Irsaliye: {irsaliye_agirlik} kg"
        
        # Prepare data - use AĞIRLIK (REAL WEIGHT) only
        data = {
            'date': tarih,
            'supplier': firma,
            'waybill_no': irsaliye,
            'mesh_type': hasir_tipi,
            'dimensions': olculer,
            'piece_count': adet,
            'weight_kg': agirlik,  # AĞIRLIK (REAL WEIGHT ONLY)
            'usage_location': konum,
            'notes': notes
        }
        
        # Insert
        response = client.table('mesh_logs').insert(data).execute()
        
        if response.data:
            added += 1
            if added % 10 == 0:
                print(f"  Progress: {added} records...")
            
    except Exception as e:
        print(f"  Error row {idx}: {e}")

print(f"\n{'='*60}")
print("IMPORT COMPLETE")
print("="*60)
print(f"Successfully added: {added} mesh records")
print(f"Total REAL WEIGHT (AGIRLIK): {total_weight:,.1f} kg")
print(f"\nExpected: 1,689,860 kg")

# Verify in Supabase
response = client.table('mesh_logs').select('*').execute()
if response.data:
    df_check = pd.DataFrame(response.data)
    supabase_total = df_check['weight_kg'].sum()
    print(f"\nVerified in Supabase:")
    print(f"  Records: {len(df_check)}")
    print(f"  Total weight_kg: {supabase_total:,.1f} kg")
    
    difference = abs(supabase_total - 1689860)
    if difference < 10:
        print(f"\nSUCCESS! Weight matches expected (difference: {difference:.1f} kg)")
    else:
        print(f"\nDifference from expected: {difference:,.1f} kg")

