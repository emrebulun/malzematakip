import os
import time
import toml
from supabase import create_client

def get_supabase_client():
    # Try to read from .streamlit/secrets.toml
    try:
        secrets_path = os.path.join(os.getcwd(), ".streamlit", "secrets.toml")
        if os.path.exists(secrets_path):
            secrets = toml.load(secrets_path)
            url = secrets["supabase"]["url"]
            key = secrets["supabase"]["anon_key"]
            return create_client(url, key)
        else:
            print("secrets.toml not found!")
            return None
    except Exception as e:
        print(f"Error loading secrets: {e}")
        return None

def remove_duplicates():
    supabase = get_supabase_client()
    if not supabase:
        return

    print("============================================================")
    print("CLEANING DUPLICATE REBAR RECORDS")
    print("============================================================")
    
    # 1. Tüm demir kayıtlarını çek
    all_records = []
    offset = 0
    limit = 1000
    
    while True:
        response = supabase.table('rebar_logs').select('*').range(offset, offset + limit - 1).execute()
        records = response.data
        if not records:
            break
        all_records.extend(records)
        offset += limit
        print(f"Fetched {len(all_records)} records...")
        
    print(f"Total records in DB: {len(all_records)}")
    
    # 2. Mükerrerleri Bul
    seen = {}
    duplicates = []
    unique_count = 0
    
    for record in all_records:
        # Benzersiz Anahtar
        waybill = str(record.get('waybill_no', '')).strip().upper().replace(' ', '')
        supplier = str(record.get('supplier', '')).strip().upper().replace(' ', '')
        date = record.get('date')
        weight = float(record.get('total_weight_kg', 0))
        
        # Key: Tarih + İrsaliye + Firma
        # Aynı irsaliye farklı tarihlerde olmaz
        key = f"{date}_{waybill}_{supplier}"
        
        if key in seen:
            # Bu kayıt zaten var, silinecekler listesine ekle
            duplicates.append(record['id'])
        else:
            # İlk kez görüyoruz, sakla
            seen[key] = record
            unique_count += 1
            
    print(f"Unique records: {unique_count}")
    print(f"Found {len(duplicates)} duplicate records to delete.")
    
    if not duplicates:
        print("No duplicates found!")
        return

    # 3. Silme İşlemi
    print("Deleting duplicates...")
    batch_size = 100
    for i in range(0, len(duplicates), batch_size):
        batch = duplicates[i:i+batch_size]
        supabase.table('rebar_logs').delete().in_('id', batch).execute()
        print(f"Deleted {i + len(batch)}/{len(duplicates)}")
        time.sleep(0.2)
        
    print("Cleanup complete!")

if __name__ == "__main__":
    remove_duplicates()
