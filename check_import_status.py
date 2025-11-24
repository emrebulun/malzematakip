"""Check import status"""

from supabase import create_client
import pandas as pd

client = create_client(
    'https://xmlnpyrgxlvyzphzqeug.supabase.co',
    'sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b'
)

print("Checking import status...")

# Concrete
response = client.table('concrete_logs').select('quantity_m3').execute()
if response.data:
    df = pd.DataFrame(response.data)
    print(f"\nBeton:")
    print(f"  Kayitlar: {len(df):,}")
    print(f"  Toplam: {df['quantity_m3'].sum():,.2f} m3")
    print(f"  Hedef: 54,124.80 m3")
    
    progress = (df['quantity_m3'].sum() / 54124.80) * 100
    print(f"  Ilerleme: {progress:.1f}%")

# Demir
response = client.table('rebar_logs').select('total_weight_kg').execute()
if response.data:
    df = pd.DataFrame(response.data)
    print(f"\nDemir:")
    print(f"  Kayitlar: {len(df):,}")
    print(f"  Toplam: {df['total_weight_kg'].sum():,.0f} kg")

# Hasir
response = client.table('mesh_logs').select('weight_kg').execute()
if response.data:
    df = pd.DataFrame(response.data)
    print(f"\nHasir:")
    print(f"  Kayitlar: {len(df):,}")
    print(f"  Toplam: {df['weight_kg'].sum():,.0f} kg")



