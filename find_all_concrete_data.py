"""Find all concrete data in Excel file"""

import pandas as pd

file_path = r"C:\Users\emreb\Desktop\BETON-997.xlsx"

print("="*60)
print("ANALYZING BETON EXCEL FILE")
print("="*60)

# Get all sheet names
xl_file = pd.ExcelFile(file_path)
print(f"\nSheet names: {xl_file.sheet_names}")

# Check each sheet
for sheet in xl_file.sheet_names:
    print(f"\n{'='*60}")
    print(f"SHEET: {sheet}")
    print("="*60)
    
    try:
        # Try different header positions
        for header_pos in [0, 1, 2]:
            print(f"\n--- Header at row {header_pos} ---")
            df = pd.read_excel(file_path, sheet_name=sheet, header=header_pos, nrows=10)
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            
            # Try to find MİKTAR column
            miktar_cols = [col for col in df.columns if 'MIKTAR' in str(col).upper() or 'M3' in str(col).upper() or 'M³' in str(col).upper()]
            if miktar_cols:
                print(f"Found quantity columns: {miktar_cols}")
                
                # Read all data with this header
                df_full = pd.read_excel(file_path, sheet_name=sheet, header=header_pos)
                print(f"Total rows: {len(df_full)}")
                
                # Try to sum
                for col in miktar_cols:
                    try:
                        df_full[col] = pd.to_numeric(df_full[col], errors='coerce')
                        total = df_full[col].sum()
                        non_null = df_full[col].notna().sum()
                        print(f"  {col}: {non_null} values, Total: {total:,.2f}")
                    except Exception as e:
                        print(f"  {col}: Error - {e}")
                
                break  # Found the right header
                
    except Exception as e:
        print(f"Error reading sheet {sheet}: {e}")

# Check for specific large sum
print("\n\n" + "="*60)
print("SEARCHING FOR TOTAL = 54,124.80")
print("="*60)

for sheet in xl_file.sheet_names:
    try:
        for header_pos in range(5):  # Try first 5 rows as header
            df = pd.read_excel(file_path, sheet_name=sheet, header=header_pos)
            
            for col in df.columns:
                if df[col].dtype in ['float64', 'int64'] or 'MIKTAR' in str(col).upper():
                    try:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        total = df[col].sum()
                        if abs(total - 54124.80) < 100:  # Within 100 of target
                            print(f"\n✓ FOUND in sheet '{sheet}', header row {header_pos}, column '{col}'")
                            print(f"  Total: {total:,.2f}")
                            print(f"  Non-null values: {df[col].notna().sum()}")
                            
                            # Show first 10 rows
                            print(f"\n  First 10 rows:")
                            print(df[[col]].head(10))
                    except:
                        pass
    except:
        pass

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)



