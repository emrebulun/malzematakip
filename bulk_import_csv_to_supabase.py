"""
Bulk CSV Import to Supabase
============================
Bu script CSV dosyasından toplu veri yükleyerek Supabase'deki tüm verileri ekler.
Supabase'in 1000 kayıt limiti sorunu çözülür.

Kullanım:
    python bulk_import_csv_to_supabase.py concrete_data.csv
"""

import pandas as pd
import sys
from supabase import create_client
from typing import List, Dict
import os
from datetime import datetime

# Supabase bağlantı bilgileri
def get_supabase_client():
    """Get Supabase client from secrets or environment"""
    url = None
    key = None
    
    # Try streamlit secrets first
    try:
        import streamlit as st
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["anon_key"]
        print("✅ Supabase bilgileri Streamlit secrets'tan alındı")
    except:
        pass
    
    # Fall back to environment variables
    if not url or not key:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if url and key:
            print("✅ Supabase bilgileri environment variables'tan alındı")
    
    # Try reading from .streamlit/secrets.toml manually
    if not url or not key:
        try:
            import toml
            secrets_path = os.path.join('.streamlit', 'secrets.toml')
            if os.path.exists(secrets_path):
                secrets = toml.load(secrets_path)
                url = secrets.get('supabase', {}).get('url')
                key = secrets.get('supabase', {}).get('anon_key')
                if url and key:
                    print("✅ Supabase bilgileri .streamlit/secrets.toml'dan alındı")
        except:
            pass
    
    if not url or not key:
        print("❌ HATA: Supabase bilgileri bulunamadı!")
        print("\nŞu yöntemlerden birini kullanın:")
        print("\n1️⃣ .streamlit/secrets.toml dosyası oluşturun:")
        print('   [supabase]')
        print('   url = "https://your-project.supabase.co"')
        print('   anon_key = "your-anon-key"')
        print("\n2️⃣ Environment variables ayarlayın:")
        print('   set SUPABASE_URL=https://your-project.supabase.co')
        print('   set SUPABASE_KEY=your-anon-key')
        sys.exit(1)
    
    return create_client(url, key)


def bulk_insert_to_supabase(client, table_name: str, data_list: List[Dict], batch_size: int = 500):
    """
    Bulk insert data to Supabase in batches
    
    Args:
        client: Supabase client
        table_name: Table name (concrete_logs, rebar_logs, mesh_logs)
        data_list: List of dictionaries to insert
        batch_size: Records per batch (default 500)
    """
    total_inserted = 0
    failed = 0
    
    print(f"\n📊 Toplam {len(data_list)} kayıt yüklenecek...")
    print(f"⚙️ Batch boyutu: {batch_size}")
    print("-" * 50)
    
    # Process in batches
    for i in range(0, len(data_list), batch_size):
        batch = data_list[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(data_list) + batch_size - 1) // batch_size
        
        print(f"\n📦 Batch {batch_num}/{total_batches} işleniyor... ({len(batch)} kayıt)")
        
        try:
            response = client.table(table_name).insert(batch).execute()
            
            if response.data:
                inserted_count = len(response.data)
                total_inserted += inserted_count
                print(f"   ✅ {inserted_count} kayıt başarıyla eklendi")
            else:
                failed += len(batch)
                print(f"   ⚠️ Batch başarısız oldu")
                
        except Exception as e:
            failed += len(batch)
            print(f"   ❌ Hata: {str(e)[:100]}")
    
    print("\n" + "=" * 50)
    print(f"🎉 İşlem tamamlandı!")
    print(f"✅ Başarılı: {total_inserted} kayıt")
    print(f"❌ Başarısız: {failed} kayıt")
    print(f"📊 Toplam: {len(data_list)} kayıt")
    print("=" * 50)
    
    return {
        'total_inserted': total_inserted,
        'failed': failed,
        'total_records': len(data_list)
    }


def prepare_concrete_data(df: pd.DataFrame) -> List[Dict]:
    """Prepare concrete data for Supabase"""
    records = []
    
    # Kolon eşleştirmesi
    column_mapping = {
        'TARİH': 'date',
        'TARH': 'date',
        'FİRMA': 'supplier',
        'FRMA': 'supplier',
        'İRSALİYE NO': 'waybill_no',
        'RSALYE NO': 'waybill_no',
        'BETON SINIFI': 'concrete_class',
        'TESLİM ŞEKLİ': 'delivery_method',
        'TESLM EKL': 'delivery_method',
        'MİKTAR (m3)': 'quantity_m3',
        'MİKTAR': 'quantity_m3',
        'MKTAR': 'quantity_m3',
        'BLOK': 'location_block',
        'AÇIKLAMA': 'notes',
        'AIKLAMA': 'notes'
    }
    
    # Rename columns
    df_renamed = df.copy()
    for old_col, new_col in column_mapping.items():
        if old_col in df_renamed.columns:
            df_renamed[new_col] = df_renamed[old_col]
    
    # Required columns
    required_cols = ['date', 'supplier', 'waybill_no', 'concrete_class', 
                    'delivery_method', 'quantity_m3', 'location_block', 'notes']
    
    for _, row in df_renamed.iterrows():
        try:
            # Convert date
            date_val = pd.to_datetime(row.get('date'))
            if pd.isna(date_val):
                continue
            
            # Get quantity
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
            
            # Firma belirleme (irsaliye numarasına göre)
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
            print(f"⚠️ Satır atlandı: {e}")
            continue
    
    return records


def main():
    """Main function"""
    print("\n" + "=" * 50)
    print("🏗️  CSV TO SUPABASE BULK IMPORT")
    print("=" * 50)
    
    # Check if CSV file is provided
    if len(sys.argv) < 2:
        print("\n❌ Kullanım: python bulk_import_csv_to_supabase.py <csv_dosyasi>")
        print("\nÖrnek:")
        print("   python bulk_import_csv_to_supabase.py beton_data.csv")
        print("   python bulk_import_csv_to_supabase.py concrete_import.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"\n❌ HATA: '{csv_file}' dosyası bulunamadı!")
        sys.exit(1)
    
    # Get table name (default to concrete_logs)
    table_name = 'concrete_logs'
    if len(sys.argv) >= 3:
        table_name = sys.argv[2]
    
    print(f"\n📄 CSV Dosyası: {csv_file}")
    print(f"📊 Hedef Tablo: {table_name}")
    
    # Get Supabase client
    print("\n🔌 Supabase'e bağlanılıyor...")
    client = get_supabase_client()
    print("✅ Bağlantı başarılı!")
    
    # Read CSV
    print(f"\n📖 CSV dosyası okunuyor...")
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ {len(df)} satır okundu")
        print(f"📋 Kolonlar: {', '.join(df.columns.tolist())}")
    except Exception as e:
        print(f"❌ CSV okuma hatası: {e}")
        sys.exit(1)
    
    # Prepare data
    print(f"\n⚙️ Veriler hazırlanıyor...")
    
    if table_name == 'concrete_logs':
        records = prepare_concrete_data(df)
    else:
        print(f"❌ Henüz sadece 'concrete_logs' destekleniyor!")
        print(f"💡 İpucu: table_name parametresini kullanın veya prepare_xxx_data fonksiyonu ekleyin")
        sys.exit(1)
    
    print(f"✅ {len(records)} kayıt hazır")
    
    # Confirm before insert
    print("\n" + "⚠️ " * 20)
    confirm = input(f"\n❓ {len(records)} kayıt Supabase'e eklenecek. Devam? (evet/hayir): ").lower()
    
    if confirm not in ['evet', 'yes', 'e', 'y']:
        print("\n❌ İşlem iptal edildi.")
        sys.exit(0)
    
    # Bulk insert
    print("\n🚀 Toplu yükleme başlıyor...")
    result = bulk_insert_to_supabase(client, table_name, records, batch_size=500)
    
    print(f"\n✅ İşlem tamamlandı!")


if __name__ == "__main__":
    main()

