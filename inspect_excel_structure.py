"""Inspect Excel file structure"""

import pandas as pd

files = {
    'BETON': r"C:\Users\emreb\Desktop\BETON-997.xlsx",
    'DEMIR': r"C:\Users\emreb\Desktop\Demir_997.xlsx",
    'HASIR': r"C:\Users\emreb\Desktop\Hasır_997.xlsx"
}

for name, path in files.items():
    print(f"\n{'='*60}")
    print(f"{name} FILE STRUCTURE")
    print('='*60)
    
    try:
        # Read first 5 rows
        df = pd.read_excel(path, nrows=5)
        print(f"Default read (nrows=5):")
        print(df)
        print(f"\nColumns: {list(df.columns)}")
        
        # Try with header=0
        print(f"\n\nWith header=0:")
        df2 = pd.read_excel(path, header=0, nrows=5)
        print(df2)
        
        # Try with header=1
        print(f"\n\nWith header=1:")
        df3 = pd.read_excel(path, header=1, nrows=5)
        print(df3)
        
    except Exception as e:
        print(f"ERROR: {e}")



