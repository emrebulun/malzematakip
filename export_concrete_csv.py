"""Export concrete data to CSV for Supabase import"""

import pandas as pd
from datetime import datetime

print("="*60)
print("EXPORTING CONCRETE TO CSV")
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

# Read Excel
print("\nReading Excel...")
df = pd.read_excel(r"C:\Users\emreb\Desktop\BETON-997.xlsx", sheet_name='Sayfa1', header=0)

df_valid = df[df['TARİH'].notna() & df['İRSALİYE NO'].notna()].copy()
df_valid['MİKTAR'] = pd.to_numeric(df_valid['MİKTAR'], errors='coerce')
df_valid = df_valid[df_valid['MİKTAR'] > 0]

print(f"Valid rows: {len(df_valid)}")

# Prepare CSV data
csv_data = []

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
            try:
                irsa_num = int(''.join(filter(str.isdigit, irsaliye)))
                firma = "ALBAYRAK BETON" if irsa_num > 14000 else "ÖZYURT BETON"
            except:
                firma = "BİLİNMİYOR"
        
        # Concrete class
        beton_sinifi = str(row.get('BETON SINIFI', 'C25')).strip().upper()
        if beton_sinifi == 'NAN' or not beton_sinifi:
            beton_sinifi = 'C25'
        
        beton_sinifi = CLASS_MAPPING.get(beton_sinifi, beton_sinifi)
        
        valid_classes = ['C16', 'C20', 'C25', 'C30', 'C35', 'C40', 'C45', 'C50']
        if beton_sinifi not in valid_classes:
            continue
        
        # Delivery
        teslim = str(row.get('TESLİM ŞEKLİ', 'MİKSERLİ')).strip().upper()
        teslim = 'POMPALI' if 'POMPA' in teslim else 'MİKSERLİ'
        
        # Quantity
        miktar = float(row['MİKTAR'])
        
        # Block
        blok = str(row.get('BLOK', '')).strip()
        if blok == 'nan' or not blok or blok == 'None':
            blok = 'Bilinmiyor'
        
        # Notes
        aciklama = str(row.get('AÇIKLAMA', '')).strip()
        if aciklama == 'nan' or not aciklama:
            aciklama = ''
        
        csv_data.append({
            'date': tarih,
            'supplier': firma,
            'waybill_no': irsaliye,
            'concrete_class': beton_sinifi,
            'delivery_method': teslim,
            'quantity_m3': miktar,
            'location_block': blok,
            'notes': aciklama if aciklama else None
        })
        
    except:
        pass

# Create DataFrame
df_export = pd.DataFrame(csv_data)

print(f"\nPrepared {len(df_export)} records")
print(f"Total: {df_export['quantity_m3'].sum():,.2f} m³")

# Export to CSV
csv_file = "concrete_import.csv"
df_export.to_csv(csv_file, index=False, encoding='utf-8')

print(f"\n✓ Exported to: {csv_file}")
print(f"\n{'='*60}")
print("MANUAL IMPORT INSTRUCTIONS")
print("="*60)
print("1. Go to Supabase Dashboard")
print("2. Open 'concrete_logs' table")
print("3. Click 'Insert' > 'Import data from CSV'")
print("4. Upload: concrete_import.csv")
print("5. Map columns automatically")
print("6. Click 'Import'")
print("\nThis will be MUCH faster than API!")


