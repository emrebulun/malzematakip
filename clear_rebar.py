import os
import toml
from supabase import create_client

def get_supabase_client():
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

def clear_rebar_table():
    supabase = get_supabase_client()
    if not supabase:
        return

    print("============================================================")
    print("CLEARING REBAR_LOGS TABLE")
    print("============================================================")
    
    # Supabase'de truncate veya delete all işlemi için where kuralı gerekir
    # Tüm id'leri çekip silmek yerine, id != '0000...' gibi bir trick kullanabiliriz
    # Veya tüm kayıtları sileriz
    
    print("Deleting all records...")
    
    # Tüm kayıtları silmek için 'neq' (not equal) filtresi kullanarak boş bir UUID olmayanları sil diyebiliriz
    # Ancak en güvenlisi batch silme
    
    while True:
        # 1000'er 1000'er sil
        response = supabase.table('rebar_logs').select('id').limit(1000).execute()
        ids = [r['id'] for r in response.data]
        
        if not ids:
            break
            
        print(f"Deleting batch of {len(ids)} records...")
        supabase.table('rebar_logs').delete().in_('id', ids).execute()
    
    print("All rebar records deleted successfully!")

if __name__ == "__main__":
    clear_rebar_table()

