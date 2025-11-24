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

def clear_concrete_table():
    supabase = get_supabase_client()
    if not supabase:
        return

    print("============================================================")
    print("CLEARING CONCRETE_LOGS TABLE")
    print("============================================================")
    
    print("Deleting all records...")
    
    while True:
        # 200'er 200'er sil (1000 fazla gelebiliyor)
        response = supabase.table('concrete_logs').select('id').limit(200).execute()
        ids = [r['id'] for r in response.data]
        
        if not ids:
            break
            
        print(f"Deleting batch of {len(ids)} records...")
        try:
            supabase.table('concrete_logs').delete().in_('id', ids).execute()
        except Exception as e:
            print(f"Error deleting batch: {e}")
            # Tek tek silmeyi dene
            for single_id in ids:
                 try:
                     supabase.table('concrete_logs').delete().eq('id', single_id).execute()
                 except:
                     pass
    
    print("All concrete records deleted successfully!")

if __name__ == "__main__":
    clear_concrete_table()

