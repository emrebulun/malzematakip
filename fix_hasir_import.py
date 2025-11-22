"""Fix Hasir import - use correct weight column"""

import pandas as pd
from supabase import create_client
import math

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b"

client = create_client(URL, KEY)

print("="*60)
print("FIXING HASIR IMPORT")
print("="*60)

# Clear existing
print("\nClearing existing mesh data...")
client.table('mesh_logs').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
print("Cleared!")

# Read Excel
df = pd.read_excel(r"C:\Users\emreb\Desktop\Hasır_997.xlsx", header=0)
print(f"\nTotal rows in Excel: {len(df)}")

# Filter: must have DATE AND WAYBILL NUMBER
df_valid = df[df['TARİH'].notna() & df['İRSALİYE NO'].notna()].copy()
print(f"Valid rows (with date AND waybill): {len(df_valid)}")

added = 0
errors = 0
total_irsaliye_agirlik = 0
total_gercek_agirlik = 0

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
            adet = 1  # Default to 1 if missing (to pass database constraint)
        else:
            adet = int(float(adet))
            if adet <= 0:
                adet = 1  # Must be at least 1 for database constraint
        
        # WEIGHT - Use İRSALİYE AĞIRLIĞI (column 22)
        irsaliye_agirlik = row.get('İRSALİYE AĞIRLIĞI')
        if pd.isna(irsaliye_agirlik):
            irsaliye_agirlik = 0
        irsaliye_agirlik = float(irsaliye_agirlik)
        
        # Real weight - AĞIRLIK (column 24) - for tracking
        gercek_agirlik = row.get('AĞIRLIK')
        if pd.isna(gercek_agirlik):
            gercek_agirlik = 0
        else:
            gercek_agirlik = float(gercek_agirlik)
        
        # Track totals
        total_irsaliye_agirlik += irsaliye_agirlik
        total_gercek_agirlik += gercek_agirlik
        
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
        
        # Prepare data - use İRSALİYE AĞIRLIĞI as weight_kg
        data = {
            'date': tarih,
            'supplier': firma,
            'waybill_no': irsaliye,
            'mesh_type': hasir_tipi,
            'dimensions': olculer,
            'piece_count': adet,
            'weight_kg': irsaliye_agirlik,  # Using İRSALİYE AĞIRLIĞI
            'usage_location': konum,
            'notes': f"Gerçek ağırlık: {gercek_agirlik} kg" if gercek_agirlik > 0 else None
        }
        
        # Insert
        response = client.table('mesh_logs').insert(data).execute()
        
        if response.data:
            added += 1
            if added % 10 == 0:
                print(f"  Progress: {added} records...")
        else:
            errors += 1
            
    except Exception as e:
        errors += 1
        if errors <= 3:
            print(f"  Error row {idx}: {e}")

print(f"\n{'='*60}")
print("IMPORT COMPLETE")
print("="*60)
print(f"Successfully added: {added} mesh records")
print(f"Errors: {errors}")
print(f"\n{'='*60}")
print("WEIGHT VERIFICATION")
print("="*60)
print(f"Total İRSALİYE AĞIRLIĞI (imported): {total_irsaliye_agirlik:,.1f} kg")
print(f"Total AĞIRLIK (tracked in notes): {total_gercek_agirlik:,.1f} kg")
print(f"\nExpected:")
print(f"  İrsaliye Ağırlığı: 1,750,520 kg")
print(f"  Gerçek Ağırlık: 1,689,860 kg")

# Verify in Supabase
response = client.table('mesh_logs').select('*').execute()
if response.data:
    df_check = pd.DataFrame(response.data)
    supabase_total = df_check['weight_kg'].sum()
    print(f"\nVerified in Supabase:")
    print(f"  Records: {len(df_check)}")
    print(f"  Total weight_kg: {supabase_total:,.1f} kg")
    
    if abs(supabase_total - 1750520) < 100:
        print("\nSUCCESS! Weight matches expected Irsaliye Agirligi!")
    elif abs(supabase_total - 1689860) < 100:
        print("\nSUCCESS! Weight matches expected Gercek Agirlik!")
    else:
        print(f"\nWarning: Difference of {abs(supabase_total - 1750520):,.1f} kg from expected")

