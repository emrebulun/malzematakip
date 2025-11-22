"""Simple Excel import - Direct column access"""

import pandas as pd
from supabase import create_client
from datetime import datetime

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b"

client = create_client(URL, KEY)

# ============ BETON ============
print("="*60)
print("IMPORTING BETON")
print("="*60)

df_beton = pd.read_excel(r"C:\Users\emreb\Desktop\BETON-997.xlsx", sheet_name='Sayfa2', header=2)
print(f"Loaded {len(df_beton)} rows")
print(f"Columns: {list(df_beton.columns)}")

beton_count = 0
for idx, row in df_beton.iterrows():
    try:
        tarih = row['TARİH']
        if pd.isna(tarih):
            continue
            
        if hasattr(tarih, 'date'):
            tarih = tarih.date().isoformat()
        else:
            tarih = pd.to_datetime(tarih).date().isoformat()
        
        irsaliye = str(row['İRSALİYE NO']).strip()
        if not irsaliye or irsaliye == 'nan':
            continue
        
        # Determine company based on waybill
        try:
            irsa_num = int(''.join(filter(str.isdigit, irsaliye)))
            firma = "ALBAYRAK BETON" if irsa_num > 14000 else "ÖZYURT BETON"
        except:
            firma = str(row.get('FİRMA', 'BİLİNMİYOR')).strip()
        
        beton_sinifi = str(row['BETON SINIFI']).strip().upper()
        if beton_sinifi == 'NAN':
            beton_sinifi = 'C25'
        
        teslim = str(row['TESLİM ŞEKLİ']).strip().upper()
        if 'POMPA' in teslim:
            teslim = 'POMPALI'
        else:
            teslim = 'MİKSERLİ'
        
        miktar = float(row['MİKTAR'])
        if miktar <= 0:
            continue
        
        blok = str(row.get('BLOK', 'Bilinmiyor')).strip()
        if blok == 'nan' or not blok:
            blok = 'Bilinmiyor'
        
        aciklama = str(row.get('AÇIKLAMA', '')).strip()
        if aciklama == 'nan':
            aciklama = None
        
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
        
        response = client.table('concrete_logs').insert(data).execute()
        if response.data:
            beton_count += 1
            if beton_count % 5 == 0:
                print(f"  Progress: {beton_count} records...")
                
    except Exception as e:
        print(f"  Error row {idx}: {e}")

print(f"SUCCESS: Added {beton_count} concrete records\n")

# ============ DEMIR ============
print("="*60)
print("IMPORTING DEMIR")
print("="*60)

df_demir = pd.read_excel(r"C:\Users\emreb\Desktop\Demir_997.xlsx", header=1)
print(f"Loaded {len(df_demir)} rows")

demir_count = 0
for idx, row in df_demir.iterrows():
    try:
        tarih = row['TARİH']
        if pd.isna(tarih):
            continue
            
        if hasattr(tarih, 'date'):
            tarih = tarih.date().isoformat()
        else:
            tarih = pd.to_datetime(tarih).date().isoformat()
        
        irsaliye = str(row['İRSALİYE NO']).strip()
        if not irsaliye or irsaliye == 'nan':
            continue
        
        firma = str(row.get('GELDİĞİ FİRMA', 'BİLİNMİYOR')).strip()
        if firma == 'nan':
            firma = 'BİLİNMİYOR'
        
        etap = str(row.get('ETAP', '')).strip()
        if etap == 'nan':
            etap = None
        
        # Get diameters - try multiple column name patterns
        diameters = {}
        total = 0
        
        # Q8
        q8 = row.get("8' LİK", 0)
        if pd.isna(q8):
            q8 = 0
        q8 = float(q8)
        diameters['q8_kg'] = q8
        total += q8
        
        # Q10
        q10 = row.get("10' LUK", 0)
        if pd.isna(q10):
            q10 = 0
        q10 = float(q10)
        diameters['q10_kg'] = q10
        total += q10
        
        # Q12
        q12 = row.get("12' LİK", 0)
        if pd.isna(q12):
            q12 = 0
        q12 = float(q12)
        diameters['q12_kg'] = q12
        total += q12
        
        # Q14
        q14 = row.get("14' LİK", 0)
        if pd.isna(q14):
            q14 = 0
        q14 = float(q14)
        diameters['q14_kg'] = q14
        total += q14
        
        # Q16
        q16 = row.get("16' LIK", 0)
        if pd.isna(q16):
            q16 = 0
        q16 = float(q16)
        diameters['q16_kg'] = q16
        total += q16
        
        # Q18
        q18 = row.get("18LİK", 0)
        if pd.isna(q18):
            q18 = 0
        q18 = float(q18)
        diameters['q18_kg'] = q18
        total += q18
        
        # Q20
        q20 = row.get("20' LIK", 0)
        if pd.isna(q20):
            q20 = 0
        q20 = float(q20)
        diameters['q20_kg'] = q20
        total += q20
        
        # Q22
        q22 = row.get("22' LİK", 0)
        if pd.isna(q22):
            q22 = 0
        q22 = float(q22)
        diameters['q22_kg'] = q22
        total += q22
        
        # Q24
        q24 = row.get("24' LİK", 0)
        if pd.isna(q24):
            q24 = 0
        q24 = float(q24)
        # Store as Q25 since we don't have Q24 in database
        diameters['q25_kg'] = q24  
        total += q24
        
        # Q25
        q25 = row.get("25' LİK", 0)
        if pd.isna(q25):
            q25 = 0
        q25 = float(q25)
        diameters['q25_kg'] += q25  # Add to Q25
        total += q25
        
        # Q28
        q28 = row.get("28' LİK", 0)
        if pd.isna(q28):
            q28 = 0
        q28 = float(q28)
        diameters['q28_kg'] = q28
        total += q28
        
        if total <= 0:
            continue
        
        data = {
            'date': tarih,
            'supplier': firma,
            'waybill_no': irsaliye,
            'project_stage': etap,
            'manufacturer': None,
            'total_weight_kg': total,
            'q8_kg': diameters.get('q8_kg', 0),
            'q10_kg': diameters.get('q10_kg', 0),
            'q12_kg': diameters.get('q12_kg', 0),
            'q14_kg': diameters.get('q14_kg', 0),
            'q16_kg': diameters.get('q16_kg', 0),
            'q18_kg': diameters.get('q18_kg', 0),
            'q20_kg': diameters.get('q20_kg', 0),
            'q22_kg': diameters.get('q22_kg', 0),
            'q25_kg': diameters.get('q25_kg', 0),
            'q28_kg': diameters.get('q28_kg', 0),
            'q32_kg': 0,
            'notes': None
        }
        
        response = client.table('rebar_logs').insert(data).execute()
        if response.data:
            demir_count += 1
            if demir_count % 20 == 0:
                print(f"  Progress: {demir_count} records...")
                
    except Exception as e:
        if demir_count < 5:  # Show first few errors
            print(f"  Error row {idx}: {e}")

print(f"SUCCESS: Added {demir_count} rebar records\n")

# SUMMARY
print("="*60)
print("IMPORT COMPLETE")
print("="*60)
print(f"Concrete: {beton_count}")
print(f"Rebar: {demir_count}")
print(f"Mesh: Already imported (63)")
print(f"TOTAL: {beton_count + demir_count + 63}")


