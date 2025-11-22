"""
Import ONLY to Supabase (No Delete)
====================================
Sadece CSV'den Supabase'e import yapar, silme yapmaz.
Önce Supabase Dashboard'dan tabloyu manuel temizleyin.

Kullanım:
    python import_only_to_supabase.py concrete_import.csv
"""

import pandas as pd
import sys
from supabase import create_client
from typing import List, Dict
import os

def get_supabase_client():
    """Get Supabase client"""
    url = None
    key = None
    
    try:
        import toml
        secrets_path = os.path.join('.streamlit', 'secrets.toml')
        if os.path.exists(secrets_path):
            secrets = toml.load(secrets_path)
            url = secrets.get('supabase', {}).get('url')
            key = secrets.get('supabase', {}).get('anon_key')
            if url and key:
                print("✅ Supabase bilgileri alındı")
    except:
        pass
    
    if not url or not key:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ HATA: Supabase bilgileri bulunamadı!")
        sys.exit(1)
    
    return create_client(url, key)


def prepare_concrete_data(df: pd.DataFrame) -> List[Dict]:
    """Prepare concrete data for Supabase"""
    records = []
    
    column_mapping = {
        'TARİH': 'date', 'TARH': 'date',
        'FİRMA': 'supplier', 'FRMA': 'supplier',
        'İRSALİYE NO': 'waybill_no', 'RSALYE NO': 'waybill_no',
        'BETON SINIFI': 'concrete_class',
        'TESLİM ŞEKLİ': 'delivery_method', 'TESLM EKL': 'delivery_method',
        'MİKTAR (m3)': 'quantity_m3', 'MİKTAR': 'quantity_m3', 'MKTAR': 'quantity_m3',
        'BLOK': 'location_block',
        'AÇIKLAMA': 'notes', 'AIKLAMA': 'notes'
    }
    
    df_renamed = df.copy()
    for old_col, new_col in column_mapping.items():
        if old_col in df_renamed.columns:
            df_renamed[new_col] = df_renamed[old_col]
    
    for _, row in df_renamed.iterrows():
        try:
            date_val = pd.to_datetime(row.get('date'))
            if pd.isna(date_val):
                continue
            
            quantity = float(row.get('quantity_m3', 0))
            if quantity <= 0:
                continue
            
            record = {
                'date': date_val.strftime('%Y-%m-%d'),
                'supplier': str(row.get('supplier', '')),
                'waybill_no': str(row.get('waybill_no', '')),
                'concrete_class': str(row.get('concrete_class', '')),
                'delivery_method': str(row.get('delivery_method', '')),
                'quantity_m3': quantity,
                'location_block': str(row.get('location_block', 'Bilinmiyor')),
                'notes': str(row.get('notes', '')) if pd.notna(row.get('notes')) else None
            }
            
            try:
                irsa_num = float(record['waybill_no'])
                if irsa_num > 14000:
                    record['supplier'] = 'ALBAYRAK BETON'
                else:
                    record['supplier'] = 'ÖZYURT BETON'
            except:
                pass
            
            records.append(record)
        except:
            continue
    
    return records


def bulk_insert(client, table_name: str, data_list: List[Dict], batch_size: int = 500):
    """Bulk insert data"""
    total_inserted = 0
    failed = 0
    
    print(f"\n📊 Toplam {len(data_list)} kayıt yüklenecek...")
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
                print(f"✅ {inserted_count} kayıt")
            else:
                failed += len(batch)
                print(f"⚠️ Başarısız")
                
        except Exception as e:
            failed += len(batch)
            print(f"❌ Hata: {str(e)[:50]}")
    
    print("\n" + "=" * 50)
    print(f"✅ Başarılı: {total_inserted} kayıt")
    print(f"❌ Başarısız: {failed} kayıt")
    print("=" * 50)
    
    return total_inserted


def main():
    print("\n" + "=" * 50)
    print("📤 IMPORT TO SUPABASE (ONLY)")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("\n❌ Kullanım: python import_only_to_supabase.py <csv_dosyasi>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    table_name = 'concrete_logs'
    
    if not os.path.exists(csv_file):
        print(f"\n❌ '{csv_file}' bulunamadı!")
        sys.exit(1)
    
    print(f"\n📄 CSV: {csv_file}")
    print(f"📊 Tablo: {table_name}")
    
    print("\n🔌 Supabase'e bağlanılıyor...")
    client = get_supabase_client()
    
    # Check current count
    try:
        response = client.table(table_name).select("id", count='exact').execute()
        current_count = response.count if hasattr(response, 'count') else 0
        print(f"📊 Mevcut kayıt sayısı: {current_count}")
        
        if current_count > 0:
            print("\n⚠️  DİKKAT: Tabloda zaten kayıt var!")
            print("   Duplicate kayıtlardan kaçınmak için önce tabloyu temizleyin:")
            print("   1. Supabase Dashboard → Table Editor → concrete_logs")
            print("   2. '...' → Truncate table")
            
            cont = input("\n❓ Yine de devam etmek istiyor musunuz? (evet/hayir): ").lower()
            if cont not in ['evet', 'yes', 'e', 'y']:
                print("❌ İşlem iptal edildi")
                sys.exit(0)
    except:
        pass
    
    print(f"\n📖 CSV okunuyor...")
    df = pd.read_csv(csv_file)
    print(f"✅ {len(df)} satır okundu")
    
    print(f"\n⚙️ Veriler hazırlanıyor...")
    records = prepare_concrete_data(df)
    print(f"✅ {len(records)} geçerli kayıt")
    
    print("\n🚀 Yükleme başlıyor...")
    total = bulk_insert(client, table_name, records)
    
    if total > 0:
        print(f"\n🎉 BAŞARILI! {total} kayıt eklendi!")
        print(f"\n💡 Streamlit'i yenileyin (R tuşu)")


if __name__ == "__main__":
    main()

