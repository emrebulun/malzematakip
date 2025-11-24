"""Complete Hasir import - all records"""

import pandas as pd
from supabase import create_client
import math

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b"

client = create_client(URL, KEY)

print("="*60)
print("CLEARING EXISTING MESH DATA")
print("="*60)

# Clear existing data
response = client.table('mesh_logs').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
print("Cleared existing mesh records")

print("\n" + "="*60)
print("IMPORTING HASIR (MESH) DATA")
print("="*60)

# Read Excel
df = pd.read_excel(r"C:\Users\emreb\Desktop\Hasır_997.xlsx", header=0)
print(f"Total rows: {len(df)}")

# Filter valid rows (with date)
df = df[df['TARİH'].notna()]
print(f"Valid rows (with date): {len(df)}")

added = 0
errors = 0
error_details = []

for idx, row in df.iterrows():
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
        
        # Waybill number
        irsaliye = row.get('İRSALİYE NO')
        if pd.isna(irsaliye):
            # Skip rows without waybill (sub-items)
            continue
        irsaliye = str(irsaliye).strip()
        
        # Mesh type
        hasir_tipi = str(row.get('HASIR TİPİ', 'Q')).strip().upper()
        if hasir_tipi == 'NAN' or not hasir_tipi:
            hasir_tipi = 'Q'
        # Ensure it's one of the valid types
        if hasir_tipi not in ['Q', 'R', 'TR']:
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
            continue
        adet = int(float(adet))
        
        if adet <= 0:
            continue
        
        # Weight - use 'AĞIRLIK' column
        agirlik = row.get('AĞIRLIK')
        if pd.isna(agirlik) or math.isnan(float(agirlik)):
            # Try alternative weight column
            agirlik = row.get('İRSALİYE AĞIRLIĞI')
            if pd.isna(agirlik):
                agirlik = 0
        
        agirlik = float(agirlik)
        
        # Usage location (ETAP or SS column)
        konum = row.get('SS')
        if pd.isna(konum) or str(konum).strip() == 'nan':
            konum = row.get('ETAP')
            if pd.isna(konum) or str(konum).strip() == 'nan':
                konum = None
            else:
                konum = str(konum).strip()
        else:
            konum = str(konum).strip()
        
        # Prepare data
        data = {
            'date': tarih,
            'supplier': firma,
            'waybill_no': irsaliye,
            'mesh_type': hasir_tipi,
            'dimensions': olculer,
            'piece_count': adet,
            'weight_kg': agirlik,
            'usage_location': konum,
            'notes': None
        }
        
        # Insert
        response = client.table('mesh_logs').insert(data).execute()
        
        if response.data:
            added += 1
            if added % 20 == 0:
                print(f"  Progress: {added} records...")
        else:
            errors += 1
            if errors <= 5:
                error_details.append(f"Row {idx}: No data returned")
            
    except Exception as e:
        errors += 1
        if errors <= 5:
            error_details.append(f"Row {idx}: {str(e)[:100]}")

print(f"\n{'='*60}")
print("IMPORT COMPLETE")
print("="*60)
print(f"Successfully added: {added} mesh records")
print(f"Errors: {errors}")

if error_details:
    print(f"\nFirst few errors:")
    for err in error_details:
        print(f"  - {err}")

print("\nMesh data is now in Supabase!")
print("Refresh your Streamlit app to see all data.")



