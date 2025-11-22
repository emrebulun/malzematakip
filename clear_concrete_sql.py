"""Clear concrete table using SQL"""

from supabase import create_client

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_secret_cLxXvF94PLb0IMicuqUNKg_vlHWVq43"  # Use service role key for delete

client = create_client(URL, KEY)

print("Clearing concrete_logs table using SQL...")

try:
    # Use RPC or direct SQL delete
    response = client.table('concrete_logs').delete().gte('id', '00000000-0000-0000-0000-000000000000').execute()
    print(f"Deleted records")
except Exception as e:
    print(f"Method 1 failed: {e}")
    
    # Try alternative: get all IDs and delete
    try:
        print("\nTrying alternative method...")
        response = client.table('concrete_logs').select('id').execute()
        if response.data:
            print(f"Found {len(response.data)} records to delete")
            
            # Delete in chunks
            chunk_size = 100
            for i in range(0, len(response.data), chunk_size):
                chunk = response.data[i:i+chunk_size]
                ids = [r['id'] for r in chunk]
                
                for id in ids:
                    try:
                        client.table('concrete_logs').delete().eq('id', id).execute()
                    except:
                        pass
                        
                print(f"  Deleted {min(i+chunk_size, len(response.data))}/{len(response.data)}")
            
            print("Done!")
    except Exception as e2:
        print(f"Method 2 also failed: {e2}")

# Verify
response = client.table('concrete_logs').select('id').limit(1).execute()
if response.data:
    print(f"\nStill {len(response.data)} records remain")
else:
    print("\nTable is now empty!")


