"""
Supabase REST API Quick Test
Just paste your anon key below and run this!
"""

# 📋 PASTE YOUR ANON KEY HERE:
ANON_KEY = "YOUR_ANON_KEY_HERE"

SUPABASE_URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"

if ANON_KEY == "YOUR_ANON_KEY_HERE":
    print("⚠️  Please get your anon key:")
    print("    1. Go to: https://supabase.com/dashboard/project/xmlnpyrgxlvyzphzqeug/settings/api")
    print("    2. Copy the 'anon public' key")
    print("    3. Paste it above (line 7)")
    print("\n    Then run: python quick_test.py")
else:
    from supabase import create_client
    
    print("🔄 Testing Supabase connection...")
    supabase = create_client(SUPABASE_URL, ANON_KEY)
    
    print("✅ Connection successful!")
    print("\n🔍 Testing concrete_logs table...")
    
    response = supabase.table('concrete_logs').select("*").limit(1).execute()
    print(f"✅ Table accessible! Records: {len(response.data)}")


