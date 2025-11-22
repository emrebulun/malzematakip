"""
Excel to CSV Converter
======================
Excel dosyalarını CSV formatına dönüştürür.
Sonra bulk_import_csv_to_supabase.py ile toplu yükleme yapabilirsiniz.

Kullanım:
    python excel_to_csv_converter.py BETON-997.xlsx
"""

import pandas as pd
import sys
import os

def excel_to_csv(excel_file: str, output_csv: str = None, sheet_name: str = 0):
    """
    Convert Excel file to CSV
    
    Args:
        excel_file: Excel dosya yolu
        output_csv: Çıktı CSV dosya yolu (None ise otomatik oluşturulur)
        sheet_name: Sheet ismi veya index (default: 0 = ilk sheet)
    """
    
    print("\n" + "=" * 50)
    print("📊 EXCEL TO CSV CONVERTER")
    print("=" * 50)
    
    # Check if file exists
    if not os.path.exists(excel_file):
        print(f"\n❌ HATA: '{excel_file}' dosyası bulunamadı!")
        return False
    
    # Auto-generate output filename
    if output_csv is None:
        base_name = os.path.splitext(excel_file)[0]
        output_csv = f"{base_name}_converted.csv"
    
    print(f"\n📄 Excel Dosyası: {excel_file}")
    print(f"💾 Çıktı CSV: {output_csv}")
    
    try:
        # Read Excel
        print(f"\n📖 Excel dosyası okunuyor...")
        
        # Try to detect sheet
        excel_file_obj = pd.ExcelFile(excel_file)
        sheet_names = excel_file_obj.sheet_names
        
        print(f"📋 Bulunan Sheet'ler: {', '.join(sheet_names)}")
        
        # Use first sheet or specified one
        if isinstance(sheet_name, int):
            selected_sheet = sheet_names[sheet_name] if sheet_name < len(sheet_names) else sheet_names[0]
        else:
            selected_sheet = sheet_name
        
        print(f"✅ Seçilen Sheet: {selected_sheet}")
        
        # Read the sheet
        df = pd.read_excel(excel_file, sheet_name=selected_sheet)
        
        print(f"✅ {len(df)} satır, {len(df.columns)} kolon okundu")
        print(f"\n📋 Kolonlar:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i}. {col}")
        
        # Save to CSV
        print(f"\n💾 CSV dosyası oluşturuluyor...")
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        
        print(f"✅ CSV başarıyla oluşturuldu: {output_csv}")
        
        # Show sample data
        print(f"\n📊 İlk 3 satır:")
        print(df.head(3).to_string())
        
        print("\n" + "=" * 50)
        print("✅ DÖNÜŞTÜRME BAŞARILI!")
        print("=" * 50)
        
        print(f"\n💡 Şimdi toplu yükleme için:")
        print(f"   python bulk_import_csv_to_supabase.py {output_csv}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    
    if len(sys.argv) < 2:
        print("\n" + "=" * 50)
        print("📊 Excel to CSV Converter")
        print("=" * 50)
        print("\n❌ Kullanım: python excel_to_csv_converter.py <excel_dosyasi> [output.csv] [sheet_name]")
        print("\nÖrnekler:")
        print("   python excel_to_csv_converter.py BETON-997.xlsx")
        print("   python excel_to_csv_converter.py BETON-997.xlsx beton_data.csv")
        print("   python excel_to_csv_converter.py BETON-997.xlsx beton_data.csv Sayfa1")
        print("\n💡 İpuçları:")
        print("   - output.csv belirtilmezse otomatik oluşturulur")
        print("   - sheet_name belirtilmezse ilk sheet kullanılır")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) >= 3 else None
    sheet_name = sys.argv[3] if len(sys.argv) >= 4 else 0
    
    success = excel_to_csv(excel_file, output_csv, sheet_name)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

