"""
Clear Supabase Table and Reimport from CSV
===========================================
Supabase tablosunu temizleyip CSV'den tekrar yükler.
Duplicate kayıt sorununu çözer.

Kullanım:
    python clear_and_reimport_supabase.py concrete_import.csv
"""

import pandas as pd
import sys
from supabase import create_client
from typing import List, Dict
import os

def get_supabase_client():
    """Get Supabase client from secrets or environment"""
    url = None
    key = None
    
    # Try reading from .streamlit/secrets.toml manually
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
    
    # Fall back to environment variables
    if not url or not key:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if url and key:
            print("✅ Supabase bilgileri environment variables'tan alındı")
    
    if not url or not key:
        print("❌ HATA: Supabase bilgileri bulunamadı!")
        sys.exit(1)
    
    return create_client(url, key)


def clear_table(client, table_name: str, auto_confirm: bool = False):
    """Clear all records from a Supabase table"""
    print(f"\n🗑️  '{table_name}' tablosu temizleniyor...")
    
    try:
        # Get current count
        response = client.table(table_name).select("id", count='exact').execute()
        current_count = response.count if hasattr(response, 'count') else 0
        
        print(f"📊 Mevcut kayıt sayısı: {current_count}")
        
        if current_count == 0:
            print("✅ Tablo zaten boş")
            return True
        
        # Confirm deletion
        if not auto_confirm:
            confirm = input(f"\n⚠️  {current_count} kayıt SİLİNECEK! Emin misiniz? (EVET/hayir): ").upper()
            
            if confirm != 'EVET':
                print("❌ İşlem iptal edildi")
                return False
        else:
            print(f"⚠️  {current_count} kayıt SİLİNECEK! (Otomatik onay ile devam ediliyor...)")
        
        # Delete all records (using a range that covers everything)
        print("🗑️  Silme işlemi başlıyor...")
        
        # Supabase'de toplu silme için: delete all where id > 0
        response = client.table(table_name).delete().gte('id', 0).execute()
        
        print("✅ Tablo temizlendi!")
        return True
        
    except Exception as e:
        print(f"❌ Temizleme hatası: {e}")
        print("\n💡 Alternatif: Supabase Dashboard'dan manuel olarak silin:")
        print(f"   1. https://supabase.com → Project → Table Editor")
        print(f"   2. '{table_name}' tablosunu açın")
        print(f"   3. Truncate veya Delete All yapın")
        return False


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
            continue
    
    return records


def bulk_insert_to_supabase(client, table_name: str, data_list: List[Dict], batch_size: int = 500):
    """Bulk insert data to Supabase in batches"""
    total_inserted = 0
    failed = 0
    
    print(f"\n📊 Toplam {len(data_list)} kayıt yüklenecek...")
    print(f"⚙️ Batch boyutu: {batch_size}")
    print("-" * 50)
    
    for i in range(0, len(data_list), batch_size):
        batch = data_list[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(data_list) + batch_size - 1) // batch_size
        
        print(f"📦 Batch {batch_num}/{total_batches} işleniyor... ({len(batch)} kayıt)", end=' ')
        
        try:
            response = client.table(table_name).insert(batch).execute()
            
            if response.data:
                inserted_count = len(response.data)
                total_inserted += inserted_count
                print(f"✅ {inserted_count} kayıt eklendi")
            else:
                failed += len(batch)
                print(f"⚠️ Başarısız")
                
        except Exception as e:
            failed += len(batch)
            print(f"❌ Hata: {str(e)[:50]}")
    
    print("\n" + "=" * 50)
    print(f"🎉 İşlem tamamlandı!")
    print(f"✅ Başarılı: {total_inserted} kayıt")
    print(f"❌ Başarısız: {failed} kayıt")
    print("=" * 50)
    
    return total_inserted


def main():
    """Main function"""
    print("\n" + "=" * 50)
    print("🔄 CLEAR & REIMPORT TO SUPABASE")
    print("=" * 50)
    
    # Check if CSV file is provided
    if len(sys.argv) < 2:
        print("\n❌ Kullanım: python clear_and_reimport_supabase.py <csv_dosyasi> [--confirm]")
        print("\nÖrnek:")
        print("   python clear_and_reimport_supabase.py concrete_import.csv")
        print("   python clear_and_reimport_supabase.py concrete_import.csv --confirm")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    table_name = 'concrete_logs'
    auto_confirm = '--confirm' in sys.argv or '-y' in sys.argv
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"\n❌ HATA: '{csv_file}' dosyası bulunamadı!")
        sys.exit(1)
    
    print(f"\n📄 CSV Dosyası: {csv_file}")
    print(f"📊 Hedef Tablo: {table_name}")
    
    # Get Supabase client
    print("\n🔌 Supabase'e bağlanılıyor...")
    client = get_supabase_client()
    print("✅ Bağlantı başarılı!")
    
    # STEP 1: Clear existing data
    if not clear_table(client, table_name, auto_confirm):
        print("\n❌ Temizleme başarısız. İşlem durduruluyor.")
        sys.exit(1)
    
    # STEP 2: Read CSV
    print(f"\n📖 CSV dosyası okunuyor...")
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ {len(df)} satır okundu")
    except Exception as e:
        print(f"❌ CSV okuma hatası: {e}")
        sys.exit(1)
    
    # STEP 3: Prepare data
    print(f"\n⚙️ Veriler hazırlanıyor...")
    records = prepare_concrete_data(df)
    print(f"✅ {len(records)} geçerli kayıt hazır")
    
    # STEP 4: Bulk insert
    print("\n🚀 Toplu yükleme başlıyor...")
    total_inserted = bulk_insert_to_supabase(client, table_name, records, batch_size=500)
    
    if total_inserted > 0:
        print(f"\n✅ BAŞARILI! {total_inserted} kayıt Supabase'e eklendi!")
        print(f"\n💡 Şimdi Streamlit uygulamasını yenileyin (R tuşu)")
        print(f"   Beklenen toplam: ~54,124.80 m³")
    else:
        print("\n⚠️ Hiçbir kayıt eklenemedi!")


if __name__ == "__main__":
    main()

