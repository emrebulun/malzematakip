"""Check real count without limit"""

from supabase import create_client

client = create_client(
    'https://xmlnpyrgxlvyzphzqeug.supabase.co',
    'sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b'
)

print("Checking REAL count...")

# Use count parameter
response = client.table('concrete_logs').select('*', count='exact').execute()

print(f"\nActual count: {response.count if hasattr(response, 'count') else 'unknown'}")
print(f"Data returned: {len(response.data) if response.data else 0}")

# Try to get just IDs with high limit
response2 = client.table('concrete_logs').select('id').limit(10000).execute()
print(f"With limit 10000: {len(response2.data) if response2.data else 0} records")

# Try pagination
print("\nTrying to count all pages...")
page_size = 1000
page = 0
total = 0

while True:
    response = client.table('concrete_logs').select('id').range(page * page_size, (page + 1) * page_size - 1).execute()
    if not response.data or len(response.data) == 0:
        break
    total += len(response.data)
    print(f"  Page {page + 1}: {len(response.data)} records (total so far: {total})")
    page += 1
    if page > 10:  # Safety limit
        print("  Stopping at page 10...")
        break

print(f"\nTotal records found: {total}")


