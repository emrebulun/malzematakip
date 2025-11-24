"""
Test Supabase REST API Connection
This is much easier than PostgreSQL direct connection!
"""

from supabase import create_client, Client

# Your Supabase project details
SUPABASE_URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
SUPABASE_ANON_KEY = "YOUR_ANON_KEY_HERE"  # Replace this!

def test_connection():
    """Test Supabase REST API connection"""
    try:
        print("🔄 Connecting to Supabase REST API...")
        print(f"   URL: {SUPABASE_URL}")
        
        # Create Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        print("✅ Connected successfully!")
        
        # Test query: Get concrete logs
        print("\n🔄 Testing query on concrete_logs table...")
        response = supabase.table('concrete_logs').select("*").limit(5).execute()
        
        print(f"✅ Query successful! Found {len(response.data)} records")
        
        if response.data:
            print("\n📊 Sample data:")
            for record in response.data[:2]:
                print(f"   - Date: {record.get('date')}, Supplier: {record.get('supplier')}")
        else:
            print("   ℹ️ No records yet (table is empty)")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("SUPABASE REST API CONNECTION TEST")
    print("=" * 60)
    
    if SUPABASE_ANON_KEY == "YOUR_ANON_KEY_HERE":
        print("\n⚠️ PLEASE UPDATE THE ANON_KEY!")
        print("\n📋 How to get it:")
        print("   1. Go to: https://supabase.com/dashboard/project/xmlnpyrgxlvyzphzqeug")
        print("   2. Click: Settings > API")
        print("   3. Copy: 'anon public' key")
        print("   4. Paste it in this file (line 10)")
    else:
        test_connection()





