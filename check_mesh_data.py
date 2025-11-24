"""Check current mesh data in Supabase"""

from supabase import create_client
import pandas as pd

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b"

print("Connecting to Supabase...")
client = create_client(URL, KEY)

print("\n" + "="*60)
print("CURRENT MESH DATA IN SUPABASE")
print("="*60)

response = client.table('mesh_logs').select('*').execute()
print(f"Total mesh records: {len(response.data)}")

if response.data:
    df = pd.DataFrame(response.data)
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nFirst 5 records:")
    print(df[['date', 'supplier', 'waybill_no', 'mesh_type', 'piece_count', 'weight_kg']].head())
    
    print(f"\n\nSummary:")
    print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"  Suppliers: {df['supplier'].unique()}")
    print(f"  Total pieces: {df['piece_count'].sum()}")
    print(f"  Total weight: {df['weight_kg'].sum():.1f} kg")

print("\n" + "="*60)
print("EXCEL FILE CHECK")
print("="*60)

# Try to find the file
import os

possible_paths = [
    r"C:\Users\emreb\Desktop\Hasır_997.xlsx",
    r"C:\Users\emreb\Desktop\Hasir_997.xlsx",
    r"C:\Users\emreb\Downloads\Hasır_997.xlsx",
    r"C:\Users\emreb\Documents\Hasır_997.xlsx",
]

found = False
for path in possible_paths:
    if os.path.exists(path):
        print(f"\nFOUND: {path}")
        df_excel = pd.read_excel(path)
        print(f"Excel rows: {len(df_excel)}")
        print(f"Valid rows (with date): {len(df_excel[df_excel['TARİH'].notna()])}")
        found = True
        break

if not found:
    print("\nFILE NOT FOUND!")
    print("Please provide the correct path to Hasır_997.xlsx file.")
    print("\nCurrent working directory:")
    print(os.getcwd())



