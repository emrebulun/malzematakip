"""
Import directly from Excel to Supabase
Handles all column mappings and data cleaning correctly
"""

import pandas as pd
import sys
from supabase import create_client
from typing import List, Dict
import os

def get_supabase_client():
    """Get Supabase client"""
    try:
        import toml
        secrets_path = os.path.join('.streamlit', 'secrets.toml')
        if os.path.exists(secrets_path):
            secrets = toml.load(secrets_path)
            url = secrets.get('supabase', {}).get('url')
            key = secrets.get('supabase', {}).get('anon_key')
            if url and key:
                return create_client(url, key)
    except:
        pass
    
    print("❌ Supabase bilgileri bulunamadı!")
    sys.exit(1)


def prepare_data_from_excel(excel_file: str, sheet_name: str = 'Sayfa1') -> List[Dict]:
    """Read and prepare data directly from Excel"""
    print(f"📖 Excel dosyası okunuyor: {excel_file}")
    
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    print(f"✅ {len(df)} satır okundu")
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Find correct columns
    date_col = None
    for col in df.columns:
        if 'TAR' in col.upper():
            date_col = col
            break
    
    firma_col = None
    for col in df.columns:
        if 'FİRMA' in col or 'FRMA' in col:
            firma_col = col
            break
    
    irsa_col = None
    for col in df.columns:
        if 'RSALYE' in col:
            irsa_col = col
            break
    
    class_col = None
    for col in df.columns:
        if 'BETON' in col and 'SINIF' in col:
            class_col = col
            break
    
    method_col = None
    for col in df.columns:
        if 'TESL' in col or 'EKL' in col:
            method_col = col
            break
    
    qty_col = None
    for col in df.columns:
        if 'KTAR' in col:
            qty_col = col
            break
    
    blok_col = None
    for col in df.columns:
        if col.strip().upper() == 'BLOK':
            blok_col = col
            break
    
    aciklama_col = None
    for col in df.columns:
        if 'AÇIKLAMA' in col or 'AIKLAMA' in col:
            if 'AÇIKLAMA2' not in col:  # Skip merged columns
                aciklama_col = col
                break
    
    print(f"\n📋 Bulunan kolonlar:")
    print(f"   TARİH: {date_col}")
    print(f"   FİRMA: {firma_col}")
    print(f"   İRSALİYE: {irsa_col}")
    print(f"   SINIF: {class_col}")
    print(f"   TESLİM: {method_col}")
    print(f"   MİKTAR: {qty_col}")
    print(f"   BLOK: {blok_col}")
    print(f"   AÇIKLAMA: {aciklama_col}")
    
    # Prepare records
    records = []
    skipped = 0
    
    for idx, row in df.iterrows():
        try:
            # Get date
            date_val = pd.to_datetime(row.get(date_col))
            if pd.isna(date_val):
                skipped += 1
                continue
            
            # Get quantity
            qty = pd.to_numeric(row.get(qty_col), errors='coerce')
            if pd.isna(qty) or qty <= 0:
                skipped += 1
                continue
            
            # Build record
            record = {
                'date': date_val.strftime('%Y-%m-%d'),
                'supplier': str(row.get(firma_col, '')) if pd.notna(row.get(firma_col)) else '',
                'waybill_no': str(row.get(irsa_col, '')) if pd.notna(row.get(irsa_col)) else '',
                'concrete_class': str(row.get(class_col, '')) if pd.notna(row.get(class_col)) else '',
                'delivery_method': str(row.get(method_col, '')) if pd.notna(row.get(method_col)) else '',
                'quantity_m3': float(qty),
                'location_block': str(row.get(blok_col, 'Bilinmiyor')) if pd.notna(row.get(blok_col)) else 'Bilinmiyor',
                'notes': str(row.get(aciklama_col, '')) if pd.notna(row.get(aciklama_col)) else None
            }
            
            # Fix supplier based on waybill
            try:
                irsa_num = float(record['waybill_no'])
                if irsa_num > 14000:
                    record['supplier'] = 'ALBAYRAK BETON'
                else:
                    record['supplier'] = 'ÖZYURT BETON'
            except:
                pass
            
            records.append(record)
            
        except Exception as e:
            skipped += 1
            continue
    
    print(f"\n✅ {len(records)} geçerli kayıt hazır")
    print(f"⚠️ {skipped} satır atlandı (boş veya hatalı)")
    
    # Calculate total
    total_m3 = sum(r['quantity_m3'] for r in records)
    print(f"📊 Toplam miktar: {total_m3:.2f} m³")
    
    return records


def bulk_insert(client, table_name: str, data_list: List[Dict], batch_size: int = 500):
    """Bulk insert"""
    total_inserted = 0
    
    print(f"\n🚀 {len(data_list)} kayıt yükleniyor...")
    print("-" * 50)
    
    for i in range(0, len(data_list), batch_size):
        batch = data_list[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(data_list) + batch_size - 1) // batch_size
        
        print(f"📦 Batch {batch_num}/{total_batches} ({len(batch)} kayıt)... ", end='')
        
        try:
            response = client.table(table_name).insert(batch).execute()
            if response.data:
                inserted_count = len(response.data)
                total_inserted += inserted_count
                print(f"✅ {inserted_count}")
        except Exception as e:
            print(f"❌ {str(e)[:50]}")
    
    print("\n" + "=" * 50)
    print(f"✅ {total_inserted} kayıt eklendi")
    print("=" * 50)
    
    return total_inserted


def main():
    if len(sys.argv) < 2:
        print("❌ Kullanım: python import_excel_direct.py <excel_dosyasi> [--force]")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    force = '--force' in sys.argv or '-f' in sys.argv
    
    if not os.path.exists(excel_file):
        print(f"❌ '{excel_file}' bulunamadı!")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("📊 EXCEL → SUPABASE DIRECT IMPORT")
    print("=" * 50)
    
    # Prepare data
    records = prepare_data_from_excel(excel_file)
    
    # Connect
    print("\n🔌 Supabase'e bağlanılıyor...")
    client = get_supabase_client()
    
    # Check existing
    try:
        response = client.table('concrete_logs').select("id", count='exact').execute()
        current = response.count if hasattr(response, 'count') else 0
        print(f"📊 Mevcut kayıt: {current}")
        
        if current > 0:
            if not force:
                print("\n⚠️ DİKKAT: Tabloda kayıt var!")
                print("   Önce temizleyin (Supabase Dashboard → Truncate)")
                cont = input("\n❓ Devam? (evet/hayir): ").lower()
                if cont not in ['evet', 'yes', 'e', 'y']:
                    sys.exit(0)
            else:
                print(f"\n⚠️ DİKKAT: Tabloda {current} kayıt var ama --force ile devam ediliyor...")
    except:
        pass
    
    # Insert
    total = bulk_insert(client, 'concrete_logs', records)
    
    if total > 0:
        print(f"\n🎉 BAŞARILI! {total} kayıt eklendi!")
        print(f"💡 Streamlit'i yenileyin (R)")


if __name__ == "__main__":
    main()

