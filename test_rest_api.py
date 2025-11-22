"""Quick test of Supabase REST API"""
# -*- coding: utf-8 -*-

import sys
sys.stdout.reconfigure(encoding='utf-8')

from supabase import create_client

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b"

print(">> Testing Supabase REST API connection...")
print(f"   URL: {URL}")

try:
    client = create_client(URL, KEY)
    print("SUCCESS: Client created!")
    
    print("\n>> Testing concrete_logs table query...")
    response = client.table('concrete_logs').select("*").limit(5).execute()
    
    print(f"SUCCESS: Query completed!")
    print(f"Records found: {len(response.data)}")
    
    if response.data:
        print("\nSample records:")
        for record in response.data[:2]:
            print(f"   - Date: {record.get('date')}, Supplier: {record.get('supplier')}")
    else:
        print("   INFO: Table is empty (no records yet)")
    
    print("\nSUCCESS! REST API is working perfectly!")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

