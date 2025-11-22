"""Continue import from where it stopped"""

import pandas as pd
from supabase import create_client
import time

URL = "https://xmlnpyrgxlvyzphzqeug.supabase.co"
KEY = "sb_publishable_nDOGbGADNR1y1Poz2_cJZg_t16JYq3b"

client = create_client(URL, KEY)

print("DEVAM EDİYOR...")

# Get existing waybills
print("\nMevcut kayitlar kontrol ediliyor...")
response = client.table('concrete_logs').select('waybill_no,supplier').execute()
existing = set()
if response.data:
    for r in response.data:
        existing.add((r['waybill_no'], r['supplier']))
print(f"Mevcut: {len(existing)} kayit")

# Read CSV
df = pd.read_csv("concrete_import.csv")
records = df.to_dict('records')

# Filter out existing
new_records = []
for r in records:
    if (r['waybill_no'], r['supplier']) not in existing:
        new_records.append(r)

print(f"Eklenecek: {len(new_records)} kayit")

if len(new_records) == 0:
    print("\nTum kayitlar zaten eklenmis!")
    
    # Final check
    response = client.table('concrete_logs').select('quantity_m3').execute()
    df_check = pd.DataFrame(response.data)
    print(f"\nToplam: {len(df_check)} kayit, {df_check['quantity_m3'].sum():.2f} m3")
    exit()

# Insert remaining
batch_size = 100
inserted = 0

print(f"\nEkleniyor ({batch_size}'lik gruplar)...")

for i in range(0, len(new_records), batch_size):
    batch = new_records[i:i+batch_size]
    
    try:
        response = client.table('concrete_logs').insert(batch).execute()
        if response.data:
            inserted += len(response.data)
            progress = ((len(existing) + inserted) / len(records)) * 100
            print(f"  {inserted}/{len(new_records)} ({progress:.1f}% toplam)")
        time.sleep(0.8)
        
    except Exception as e:
        print(f"  Hata: {str(e)[:60]}")
        time.sleep(2)

print(f"\nTamamlandi! {inserted} yeni kayit eklendi")

# Final verify
response = client.table('concrete_logs').select('quantity_m3').execute()
df_final = pd.DataFrame(response.data)
total = df_final['quantity_m3'].sum()

print(f"\nSON DURUM:")
print(f"  Kayitlar: {len(df_final):,}")
print(f"  Toplam: {total:,.2f} m3")
print(f"  Hedef: 54,124.80 m3")

if abs(total - 54124.80) < 200:
    print(f"\n  BASARILI!")
else:
    print(f"\n  Fark: {abs(total - 54124.80):,.2f} m3")


