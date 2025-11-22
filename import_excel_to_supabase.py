"""
Import Excel Data to Supabase
Loads existing Excel files into Supabase database
"""

import pandas as pd
import os
from datetime import datetime
from supabase import create_client
import sys

# Supabase credentials
URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b"

# Excel file paths
BETON_FILE = r"C:\Users\emreb\Desktop\BETON-997.xlsx"
DEMIR_FILE = r"C:\Users\emreb\Desktop\Demir_997.xlsx"
HASIR_FILE = r"C:\Users\emreb\Desktop\Hasır_997.xlsx"

def create_supabase_client():
    """Create Supabase client"""
    return create_client(URL, KEY)

def import_beton_data(client, file_path):
    """Import concrete data from Excel"""
    print("\n" + "="*60)
    print("IMPORTING CONCRETE DATA (BETON)")
    print("="*60)
    
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return 0
    
    try:
        # Read Excel from Sayfa2 sheet, header at row 2 (0-indexed)
        df = pd.read_excel(file_path, sheet_name='Sayfa2', header=2)
        print(f"Loaded {len(df)} rows from Excel (Sheet: Sayfa2)")
        
        # Show columns
        print(f"Columns: {list(df.columns)}")
        
        # Clean and map columns
        column_mapping = {}
        for col in df.columns:
            col_clean = str(col).strip().upper()
            if 'TAR' in col_clean or 'DATE' in col_clean:
                column_mapping[col] = 'TARİH'
            elif 'İRSAL' in col_clean or 'WAYBILL' in col_clean:
                column_mapping[col] = 'İRSALİYE NO'
            elif 'FİRMA' in col_clean or 'SUPPLIER' in col_clean or 'COMPANY' in col_clean:
                column_mapping[col] = 'FİRMA'
            elif 'SINIF' in col_clean or 'CLASS' in col_clean:
                column_mapping[col] = 'BETON SINIFI'
            elif 'TESLİM' in col_clean or 'DELIVERY' in col_clean or 'POMPA' in col_clean:
                column_mapping[col] = 'TESLİM ŞEKLİ'
            elif 'MİKTAR' in col_clean or 'QUANTITY' in col_clean or 'M3' in col_clean or 'M³' in col_clean:
                column_mapping[col] = 'MİKTAR'
            elif 'BLOK' in col_clean or 'BLOCK' in col_clean or 'KONUM' in col_clean:
                column_mapping[col] = 'BLOK'
        
        df = df.rename(columns=column_mapping)
        print(f"Mapped columns: {list(df.columns)}")
        
        # Process data
        records_added = 0
        errors = 0
        
        for idx, row in df.iterrows():
            try:
                # Get date
                tarih = row.get('TARİH')
                if pd.isna(tarih):
                    continue
                
                if isinstance(tarih, str):
                    tarih = pd.to_datetime(tarih).date()
                elif hasattr(tarih, 'date'):
                    tarih = tarih.date()
                
                # Get waybill number
                irsaliye = str(row.get('İRSALİYE NO', '')).strip()
                if not irsaliye or irsaliye == 'nan':
                    continue
                
                # Determine company based on waybill number
                try:
                    irsaliye_num = int(''.join(filter(str.isdigit, irsaliye)))
                    firma = "ALBAYRAK BETON" if irsaliye_num > 14000 else "ÖZYURT BETON"
                except:
                    firma = str(row.get('FİRMA', 'BİLİNMİYOR')).strip()
                
                # Get concrete class
                beton_sinifi = str(row.get('BETON SINIFI', 'C25')).strip().upper()
                if not beton_sinifi or beton_sinifi == 'NAN':
                    beton_sinifi = 'C25'
                
                # Get delivery method
                teslim = str(row.get('TESLİM ŞEKLİ', 'MİKSERLİ')).strip().upper()
                if 'POMPA' in teslim:
                    teslim = 'POMPALI'
                else:
                    teslim = 'MİKSERLİ'
                
                # Get quantity
                miktar = row.get('MİKTAR', 0)
                if pd.isna(miktar):
                    miktar = 0
                miktar = float(miktar)
                
                if miktar <= 0:
                    continue
                
                # Get block
                blok = str(row.get('BLOK', '')).strip()
                if not blok or blok == 'nan' or blok == 'None':
                    blok = 'Bilinmiyor'
                
                # Prepare data
                data = {
                    'date': tarih.isoformat(),
                    'supplier': firma,
                    'waybill_no': irsaliye,
                    'concrete_class': beton_sinifi,
                    'delivery_method': teslim,
                    'quantity_m3': miktar,
                    'location_block': blok,
                    'notes': None
                }
                
                # Insert to Supabase
                response = client.table('concrete_logs').insert(data).execute()
                
                if response.data:
                    records_added += 1
                    if records_added % 10 == 0:
                        print(f"  Progress: {records_added} records added...")
                else:
                    errors += 1
                    
            except Exception as e:
                errors += 1
                if errors <= 5:  # Show first 5 errors only
                    print(f"  Error on row {idx}: {e}")
        
        print(f"\nSUCCESS: Added {records_added} concrete records")
        print(f"Errors: {errors}")
        return records_added
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 0

def import_demir_data(client, file_path):
    """Import rebar (iron) data from Excel"""
    print("\n" + "="*60)
    print("IMPORTING REBAR DATA (DEMİR)")
    print("="*60)
    
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return 0
    
    try:
        # Read Excel with header at row 1
        df = pd.read_excel(file_path, header=1)
        print(f"Loaded {len(df)} rows from Excel")
        print(f"Columns: {list(df.columns)}")
        
        records_added = 0
        errors = 0
        
        for idx, row in df.iterrows():
            try:
                # Find date column
                tarih = None
                for col in df.columns:
                    if 'TAR' in str(col).upper() or 'DATE' in str(col).upper():
                        tarih = row.get(col)
                        break
                
                if pd.isna(tarih):
                    continue
                
                if isinstance(tarih, str):
                    tarih = pd.to_datetime(tarih).date()
                elif hasattr(tarih, 'date'):
                    tarih = tarih.date()
                
                # Find waybill
                irsaliye = None
                for col in df.columns:
                    if 'İRSAL' in str(col).upper() or 'WAYBILL' in str(col).upper():
                        irsaliye = str(row.get(col, '')).strip()
                        break
                
                if not irsaliye or irsaliye == 'nan':
                    continue
                
                # Find supplier
                firma = 'BİLİNMİYOR'
                for col in df.columns:
                    if 'FİRMA' in str(col).upper() or 'SUPPLIER' in str(col).upper():
                        firma = str(row.get(col, 'BİLİNMİYOR')).strip()
                        break
                
                # Find project stage
                etap = None
                for col in df.columns:
                    if 'ETAP' in str(col).upper() or 'STAGE' in str(col).upper():
                        etap = str(row.get(col, '')).strip()
                        break
                
                # Find manufacturer
                uretici = None
                for col in df.columns:
                    if 'ÜRETİCİ' in str(col).upper() or 'MANUFACTURER' in str(col).upper():
                        uretici = str(row.get(col, '')).strip()
                        break
                
                # Find diameter columns (Q8, Q10, etc.)
                diameters = {}
                total = 0
                
                for col in df.columns:
                    col_upper = str(col).upper().strip()
                    # Check if column is Q followed by numbers
                    if col_upper.startswith('Q') and len(col_upper) >= 2:
                        try:
                            diam_str = ''.join(filter(str.isdigit, col_upper))
                            if diam_str:
                                diam = int(diam_str)
                                if diam in [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]:
                                    val = row.get(col, 0)
                                    if not pd.isna(val):
                                        val = float(val)
                                        diameters[f'q{diam}_kg'] = val
                                        total += val
                        except:
                            pass
                
                if total <= 0:
                    continue
                
                # Prepare data
                data = {
                    'date': tarih.isoformat(),
                    'supplier': firma,
                    'waybill_no': irsaliye,
                    'project_stage': etap if etap and etap != 'nan' else None,
                    'manufacturer': uretici if uretici and uretici != 'nan' else None,
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
                    'q32_kg': diameters.get('q32_kg', 0),
                    'notes': None
                }
                
                # Insert to Supabase
                response = client.table('rebar_logs').insert(data).execute()
                
                if response.data:
                    records_added += 1
                    if records_added % 10 == 0:
                        print(f"  Progress: {records_added} records added...")
                else:
                    errors += 1
                    
            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"  Error on row {idx}: {e}")
        
        print(f"\nSUCCESS: Added {records_added} rebar records")
        print(f"Errors: {errors}")
        return records_added
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 0

def import_hasir_data(client, file_path):
    """Import mesh data from Excel"""
    print("\n" + "="*60)
    print("IMPORTING MESH DATA (HASIR)")
    print("="*60)
    
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return 0
    
    try:
        # Read Excel with header at row 0
        df = pd.read_excel(file_path, header=0)
        print(f"Loaded {len(df)} rows from Excel")
        print(f"Columns: {list(df.columns)}")
        
        # Filter out rows where TAR�H is NaT (null)
        df = df[df['TARİH'].notna()]
        print(f"After filtering: {len(df)} valid rows")
        
        records_added = 0
        errors = 0
        
        for idx, row in df.iterrows():
            try:
                # Find date
                tarih = None
                for col in df.columns:
                    if 'TAR' in str(col).upper() or 'DATE' in str(col).upper():
                        tarih = row.get(col)
                        break
                
                if pd.isna(tarih):
                    continue
                
                if isinstance(tarih, str):
                    tarih = pd.to_datetime(tarih).date()
                elif hasattr(tarih, 'date'):
                    tarih = tarih.date()
                
                # Find waybill
                irsaliye = None
                for col in df.columns:
                    if 'İRSAL' in str(col).upper() or 'WAYBILL' in str(col).upper():
                        irsaliye = str(row.get(col, '')).strip()
                        break
                
                if not irsaliye or irsaliye == 'nan':
                    continue
                
                # Find supplier
                firma = 'BİLİNMİYOR'
                for col in df.columns:
                    if 'FİRMA' in str(col).upper() or 'SUPPLIER' in str(col).upper():
                        firma = str(row.get(col, 'BİLİNMİYOR')).strip()
                        break
                
                # Find mesh type
                hasir_tipi = 'Q'
                for col in df.columns:
                    col_upper = str(col).upper()
                    if 'TİP' in col_upper or 'TYPE' in col_upper:
                        tip = str(row.get(col, 'Q')).strip().upper()
                        if tip in ['Q', 'R', 'TR']:
                            hasir_tipi = tip
                        break
                
                # Find dimensions
                olculer = None
                for col in df.columns:
                    if 'ÖLÇÜ' in str(col).upper() or 'DIM' in str(col).upper():
                        olculer = str(row.get(col, '')).strip()
                        break
                
                # Find piece count
                adet = 0
                for col in df.columns:
                    col_upper = str(col).upper()
                    if 'ADET' in col_upper or 'COUNT' in col_upper or 'PIECE' in col_upper:
                        adet = row.get(col, 0)
                        if not pd.isna(adet):
                            adet = int(float(adet))
                        break
                
                if adet <= 0:
                    continue
                
                # Find weight
                agirlik = 0
                for col in df.columns:
                    col_upper = str(col).upper()
                    if 'AĞIRLIK' in col_upper or 'WEIGHT' in col_upper or 'KG' in col_upper:
                        agirlik = row.get(col, 0)
                        if not pd.isna(agirlik):
                            agirlik = float(agirlik)
                        break
                
                # Prepare data
                data = {
                    'date': tarih.isoformat(),
                    'supplier': firma,
                    'waybill_no': irsaliye,
                    'mesh_type': hasir_tipi,
                    'dimensions': olculer if olculer and olculer != 'nan' else None,
                    'piece_count': adet,
                    'weight_kg': agirlik,
                    'usage_location': None,
                    'notes': None
                }
                
                # Insert to Supabase
                response = client.table('mesh_logs').insert(data).execute()
                
                if response.data:
                    records_added += 1
                    if records_added % 10 == 0:
                        print(f"  Progress: {records_added} records added...")
                else:
                    errors += 1
                    
            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"  Error on row {idx}: {e}")
        
        print(f"\nSUCCESS: Added {records_added} mesh records")
        print(f"Errors: {errors}")
        return records_added
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 0

def main():
    """Main import function"""
    print("\n" + "="*60)
    print("EXCEL TO SUPABASE IMPORTER")
    print("="*60)
    
    # Create client
    print("\nConnecting to Supabase...")
    client = create_supabase_client()
    print("SUCCESS: Connected!")
    
    # Import data
    total_beton = import_beton_data(client, BETON_FILE)
    total_demir = import_demir_data(client, DEMIR_FILE)
    total_hasir = import_hasir_data(client, HASIR_FILE)
    
    # Summary
    print("\n" + "="*60)
    print("IMPORT COMPLETE!")
    print("="*60)
    print(f"Concrete records: {total_beton}")
    print(f"Rebar records: {total_demir}")
    print(f"Mesh records: {total_hasir}")
    print(f"TOTAL: {total_beton + total_demir + total_hasir}")
    print("\nYou can now refresh your Streamlit app to see all data!")

if __name__ == "__main__":
    main()

