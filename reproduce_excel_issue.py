import pandas as pd
from excel_uploader import ExcelValidator
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_concrete_validation():
    validator = ExcelValidator()
    
    # Create a sample DataFrame with various scenarios
    data = {
        'Tarih': [
            '2023-11-24', # Valid
            '24.11.2023', # Valid
            None,         # Missing Date - Should be skipped/error
            'Invalid',    # Invalid Date - Should be error
            '2023-11-25'  # Valid
        ],
        'Firma': ['Firma A', 'Firma B', 'Firma C', 'Firma D', 'Firma E'],
        'İrsaliye No': ['1001', '1002', '1003', '1004', '1005'],
        'Beton Sınıfı': ['C30', 'C25', 'C30', 'C30', 'C30'],
        'Miktar': [
            10.5,         # Valid float
            '12,5',       # Valid string comma
            None,         # Missing Quantity - Should be skipped/error
            0,            # Zero Quantity - Should be error
            '15.5'        # Valid string dot
        ],
        'Teslimat Şekli': ['Pompalı', 'Mikser', 'Pompalı', 'Pompalı', 'Pompalı'],
        'Blok': ['A1', 'A2', 'A3', 'A4', 'A5'],
        'Açıklama': ['Note 1', 'Note 2', 'Note 3', 'Note 4', 'Note 5']
    }
    
    df = pd.DataFrame(data)
    
    # Add some completely empty rows or sparse rows
    df.loc[len(df)] = [None, None, None, None, None, None, None, None] # Empty row
    df.loc[len(df)] = ['2023-11-26', None, None, None, None, None, None, None] # Only date
    
    with open('reproduce_output.txt', 'w', encoding='utf-8') as f:
        f.write("Original DataFrame:\n")
        f.write(str(df) + "\n")
        f.write("-" * 50 + "\n")
        
        cleaned_data, errors = validator.validate_concrete(df)
        
        f.write(f"\nCleaned Data Count: {len(cleaned_data)}\n")
        f.write("Cleaned Data:\n")
        for item in cleaned_data:
            f.write(str(item) + "\n")
            
        f.write(f"\nErrors Count: {len(errors)}\n")
        f.write("Errors:\n")
        for err in errors:
            f.write(str(err) + "\n")


    # Check what was skipped (neither in cleaned_data nor in errors)
    # This is tricky to map back exactly without row numbers, but we can infer.
    # The validator returns row numbers in errors.
    
if __name__ == "__main__":
    test_concrete_validation()
