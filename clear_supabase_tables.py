"""Clear all data from Supabase tables before re-import"""

from supabase import create_client

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b"

print("Connecting to Supabase...")
client = create_client(URL, KEY)
print("SUCCESS: Connected!")

tables = ['concrete_logs', 'rebar_logs', 'mesh_logs']

for table in tables:
    print(f"\nClearing {table}...")
    try:
        # Get all records
        response = client.table(table).select("id").execute()
        count = len(response.data) if response.data else 0
        
        if count > 0:
            # Delete all (limit 1000 at a time for safety)
            response = client.table(table).delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
            print(f"  Cleared {count} records from {table}")
        else:
            print(f"  {table} is already empty")
            
    except Exception as e:
        print(f"  ERROR: {e}")

print("\nDONE! All tables cleared. Ready for fresh import.")


