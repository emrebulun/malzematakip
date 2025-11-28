import pandas as pd
import numpy as np
from datetime import datetime
import hashlib
import re

class ExcelValidator:
    def __init__(self):
        # Standard column mappings (User friendly name -> Internal key)
        self.concrete_columns = {
            'Tarih': 'date',
            'Firma': 'supplier',
            'İrsaliye No': 'waybill_no',
            'Beton Sınıfı': 'concrete_class',
            'Miktar': 'quantity_m3',
            'Teslimat Şekli': 'delivery_method',
            'Blok': 'location_block',
            'Açıklama': 'notes'
        }
        
        self.rebar_columns = {
            'Tarih': 'date',
            'Tedarikçi': 'supplier',
            'İrsaliye No': 'waybill_no',
            'Etap': 'project_stage',
            'Üretici': 'manufacturer',
            'Notlar': 'notes'
            # Diameter columns are dynamic (Q8, Q10...)
        }
        
        self.mesh_columns = {
            'Tarih': 'date',
            'Firma': 'supplier',
            'İrsaliye No': 'waybill_no',
            'Hasır Tipi': 'mesh_type',
            'Ebatlar': 'dimensions',
            'Adet': 'piece_count',
            'Ağırlık': 'weight_kg',
            'Kullanım Yeri': 'usage_location',
            'Notlar': 'notes'
        }

    def _is_header_row(self, values, keywords, min_matches=2):
        """Check if a list of values looks like a header row."""
        row_values = [str(v).upper().strip() for v in values if pd.notna(v)]
        match_count = sum(1 for k in keywords if any(k in rv for rv in row_values))
        return match_count >= min_matches

    def _find_header_row(self, df, keywords, min_matches=2):
        """Find the header row index by looking for keywords."""
        # First check existing columns
        if self._is_header_row(df.columns, keywords, min_matches):
            return -1 # Indicates existing columns are headers
            
        for i in range(min(20, len(df))):
            if self._is_header_row(df.iloc[i], keywords, min_matches):
                return i
        return None

    def _clean_column_names(self, df):
        """Clean column names: strip whitespace, upper case, remove Unnamed."""
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df

    def _find_col(self, df, patterns):
        """Find a column matching one of the regex patterns."""
        for col in df.columns:
            for p in patterns:
                if re.search(p, col, re.IGNORECASE):
                    return col
        return None

    def _parse_date(self, val):
        """Parse date from various formats."""
        if pd.isna(val): return None
        
        if isinstance(val, datetime):
            return val.strftime('%Y-%m-%d')
            
        s_val = str(val).strip()
        if not s_val: return None
        
        # Try common formats
        formats = ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%Y.%m.%d', '%d-%m-%Y']
        for fmt in formats:
            try:
                return pd.to_datetime(s_val, dayfirst=True).strftime('%Y-%m-%d')
            except:
                continue
        return None

    def _parse_float(self, val):
        """Parse float from string with comma/dot handling."""
        if pd.isna(val): return 0.0
        if isinstance(val, (int, float)): return float(val)
        
        s_val = str(val).strip()
        if not s_val: return 0.0
        
        # Remove non-numeric chars except , .
        clean_val = re.sub(r'[^\d.,]', '', s_val)
        if not clean_val: return 0.0
        
        # 1.234,56 -> 1234.56
        if ',' in clean_val and '.' in clean_val:
            if clean_val.find('.') < clean_val.find(','): # 1.234,56
                clean_val = clean_val.replace('.', '').replace(',', '.')
            else: # 1,234.56
                clean_val = clean_val.replace(',', '')
        elif ',' in clean_val:
            clean_val = clean_val.replace(',', '.')
            
        try:
            return float(clean_val)
        except:
            return 0.0

    def validate_concrete(self, df):
        cleaned_data = []
        errors = []
        
        # 1. Find Header
        keywords = ['TARİH', 'FİRMA', 'BETON', 'SINIF', 'MİKTAR', 'İRSALİYE']
        header_idx = self._find_header_row(df, keywords)
        
        if header_idx == -1:
            # Existing columns are headers
            pass
        else:
            if header_idx is None:
                # Fallback: Check if first row is header
                header_idx = 0
                
            # Reset dataframe to start from header
            df = df.iloc[header_idx:].reset_index(drop=True)
            df.columns = df.iloc[0]
            df = df.iloc[1:].reset_index(drop=True)
        
        self._clean_column_names(df)
        
        # 2. Map Columns
        col_map = {}
        col_map['date'] = self._find_col(df, [r'TAR[İI]H', r'DATE'])
        col_map['supplier'] = self._find_col(df, [r'F[İI]RMA', r'TEDAR[İI]K', r'BETONCU'])
        col_map['waybill_no'] = self._find_col(df, [r'[İI]RSAL[İI]YE', r'F[İI][ŞS]'])
        col_map['concrete_class'] = self._find_col(df, [r'SINIF', r'C[İI]NS', r'DAYANIM'])
        col_map['quantity_m3'] = self._find_col(df, [r'M[İI]KTAR', r'M3', r'ADET'])
        col_map['delivery_method'] = self._find_col(df, [r'TESL[İI]M', r'POMPA'])
        col_map['location_block'] = self._find_col(df, [r'BLOK', r'YER', r'MAHAL'])
        col_map['notes'] = self._find_col(df, [r'AÇIKLAMA', r'NOT'])
        
        # Critical columns check
        if not col_map['date']:
            return [], ["'Tarih' sütunu bulunamadı."]
        if not col_map['quantity_m3']:
            return [], ["'Miktar' (m3) sütunu bulunamadı."]

        valid_classes = ['C16', 'C20', 'C25', 'C30', 'C35', 'C40', 'GRO', 'ŞAP', 'KUM', 'TAS', 'TAŞ']

        for index, row in df.iterrows():
            row_num = index + 2 + (header_idx if header_idx != -1 else 0)
            try:
                # Skip empty rows
                if row.dropna().empty: continue
                
                # Skip "Total" rows
                row_str = " ".join([str(v).upper() for v in row.values if pd.notna(v)])
                if "TOPLAM" in row_str or "GENEL" in row_str: continue

                data = {}
                
                # Date
                data['date'] = self._parse_date(row.get(col_map['date']))
                if not data['date']: continue # Skip rows without valid date
                
                # Quantity
                qty = self._parse_float(row.get(col_map['quantity_m3']))
                if qty <= 0: continue # Skip rows with 0 quantity
                data['quantity_m3'] = qty
                
                # Supplier
                if col_map['supplier'] and pd.notna(row.get(col_map['supplier'])):
                    data['supplier'] = str(row.get(col_map['supplier'])).strip().upper()
                else:
                    data['supplier'] = "BİLİNMEYEN"
                
                # Concrete Class
                if col_map['concrete_class'] and pd.notna(row.get(col_map['concrete_class'])):
                    raw_class = str(row.get(col_map['concrete_class'])).strip().upper().replace(" ", "")
                    matched = next((c for c in valid_classes if c in raw_class), None)
                    data['concrete_class'] = matched if matched else "Diğer"
                else:
                    data['concrete_class'] = "Diğer"
                
                # Delivery Method
                if col_map['delivery_method'] and pd.notna(row.get(col_map['delivery_method'])):
                    d_method = str(row.get(col_map['delivery_method'])).strip().upper()
                    data['delivery_method'] = "POMPALI" if "POMPA" in d_method else "MİKSERLİ"
                else:
                    data['delivery_method'] = "MİKSERLİ"
                
                # Location & Notes
                data['location_block'] = str(row.get(col_map['location_block'])).strip() if col_map['location_block'] and pd.notna(row.get(col_map['location_block'])) else None
                data['notes'] = str(row.get(col_map['notes'])).strip() if col_map['notes'] and pd.notna(row.get(col_map['notes'])) else None
                
                # Waybill No (Critical for duplicates)
                if col_map['waybill_no'] and pd.notna(row.get(col_map['waybill_no'])):
                    wb = str(row.get(col_map['waybill_no'])).strip().upper()
                    if wb:
                        data['waybill_no'] = wb
                    else:
                        # Generate hash
                        unique_str = f"{data['date']}_{data['supplier']}_{data['concrete_class']}_{data['quantity_m3']:.2f}_{data['location_block'] or ''}"
                        data['waybill_no'] = f"AUTO-{hashlib.md5(unique_str.encode()).hexdigest()[:8]}"
                else:
                    # Generate hash
                    unique_str = f"{data['date']}_{data['supplier']}_{data['concrete_class']}_{data['quantity_m3']:.2f}_{data['location_block'] or ''}"
                    data['waybill_no'] = f"AUTO-{hashlib.md5(unique_str.encode()).hexdigest()[:8]}"

                cleaned_data.append(data)
                
            except Exception as e:
                errors.append(f"Satır {row_num}: {str(e)}")
                
        return cleaned_data, errors

    def _find_all_cols(self, df, patterns):
        """Find ALL columns matching one of the regex patterns."""
        matches = []
        for col in df.columns:
            for p in patterns:
                if re.search(p, col, re.IGNORECASE):
                    matches.append(col)
                    break 
        return matches

    def validate_rebar(self, df):
        cleaned_data = []
        errors = []
        
        # 1. Find Header
        keywords = ['TARİH', 'FİRMA', 'TEDARİK', 'İRSALİYE', 'DEMİR', 'ÇAP']
        header_idx = self._find_header_row(df, keywords)
        
        if header_idx == -1:
            pass
        else:
            if header_idx is None: header_idx = 0
                
            df = df.iloc[header_idx:].reset_index(drop=True)
            df.columns = df.iloc[0]
            df = df.iloc[1:].reset_index(drop=True)
        self._clean_column_names(df)
        
        # 2. Map Columns
        col_map = {}
        col_map['date'] = self._find_col(df, [r'TAR[İI]H', r'DATE'])
        col_map['supplier'] = self._find_col(df, [r'F[İI]RMA', r'TEDAR[İI]K', r'CAR[İI]'])
        col_map['waybill_no'] = self._find_col(df, [r'[İI]RSAL[İI]YE', r'F[İI][ŞS]'])
        col_map['project_stage'] = self._find_col(df, [r'ETAP', 'BÖLÜM', 'BLOK'])
        col_map['manufacturer'] = self._find_col(df, [r'ÜRET[İI]C[İI]', 'MARKA'])
        col_map['notes'] = self._find_col(df, [r'NOT', 'AÇIKLAMA'])
        
        if not col_map['date']: return [], ["'Tarih' sütunu bulunamadı."]
        
        # Find diameter columns (Allow multiple columns for same diameter)
        diameter_cols = {}
        for d in [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]:
            # Regex to find columns like "Q8", "8 lik", "Ø8"
            pat = rf"(^|\s|Q|Ø){d}(\s|'|’|l[ıi]k|mm|$)"
            cols = self._find_all_cols(df, [pat])
            if cols: diameter_cols[d] = cols

        for index, row in df.iterrows():
            row_num = index + 2 + (header_idx if header_idx != -1 else 0)
            try:
                if row.dropna().empty: continue
                row_str = " ".join([str(v).upper() for v in row.values if pd.notna(v)])
                if "TOPLAM" in row_str or "GENEL" in row_str: continue

                data = {}
                
                # Date
                data['date'] = self._parse_date(row.get(col_map['date']))
                if not data['date']: continue
                
                # Supplier
                data['supplier'] = str(row.get(col_map['supplier'])).strip().upper() if col_map['supplier'] and pd.notna(row.get(col_map['supplier'])) else "BİLİNMEYEN"
                
                # Other fields
                data['project_stage'] = str(row.get(col_map['project_stage'])).strip() if col_map['project_stage'] and pd.notna(row.get(col_map['project_stage'])) else None
                data['manufacturer'] = str(row.get(col_map['manufacturer'])).strip() if col_map['manufacturer'] and pd.notna(row.get(col_map['manufacturer'])) else None
                data['notes'] = str(row.get(col_map['notes'])).strip() if col_map['notes'] and pd.notna(row.get(col_map['notes'])) else ""

                # Weights
                total_weight = 0.0
                for d, cols in diameter_cols.items():
                    d_total = 0.0
                    for col in cols:
                        val = self._parse_float(row.get(col))
                        d_total += val
                    
                    data[f'q{d}_kg'] = d_total
                    total_weight += d_total
                
                # Special case for Q24 mapped to Q25
                cols_24 = self._find_all_cols(df, [r"(^|\s|Q|Ø)24(\s|'|’|l[ıi]k|mm|$)"])
                if cols_24:
                    val_24_total = 0.0
                    for col in cols_24:
                        val_24_total += self._parse_float(row.get(col))
                    
                    if val_24_total > 0:
                        data['q25_kg'] = data.get('q25_kg', 0) + val_24_total
                        total_weight += val_24_total
                        data['notes'] += f" | {val_24_total:.0f}kg Q24 (Q25'e eklendi)"

                if total_weight <= 0: continue # Skip if no weight
                
                data['total_weight_kg'] = total_weight
                data['notes'] = data['notes'].strip(" |")

                # Waybill
                if col_map['waybill_no'] and pd.notna(row.get(col_map['waybill_no'])):
                    wb = str(row.get(col_map['waybill_no'])).strip().upper()
                    if wb:
                        data['waybill_no'] = wb
                    else:
                        # Create a string representation of all weights and notes for uniqueness
                        weights_str = "_".join([f"q{d}:{data.get(f'q{d}_kg', 0)}" for d in [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32] if data.get(f'q{d}_kg', 0) > 0])
                        unique_str = f"{data['date']}_{data['supplier']}_{weights_str}_{data['project_stage'] or ''}_{data['notes'] or ''}_{index}"
                        data['waybill_no'] = f"AUTO-{hashlib.md5(unique_str.encode()).hexdigest()[:8]}"
                else:
                    # Create a string representation of all weights and notes for uniqueness
                    weights_str = "_".join([f"q{d}:{data.get(f'q{d}_kg', 0)}" for d in [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32] if data.get(f'q{d}_kg', 0) > 0])
                    unique_str = f"{data['date']}_{data['supplier']}_{weights_str}_{data['project_stage'] or ''}_{data['notes'] or ''}_{index}"
                    data['waybill_no'] = f"AUTO-{hashlib.md5(unique_str.encode()).hexdigest()[:8]}"

                data['row_num'] = row_num
                cleaned_data.append(data)
            except Exception as e:
                errors.append(f"Satır {row_num}: {str(e)}")
                
        return cleaned_data, errors

    def validate_mesh(self, df):
        cleaned_data = []
        errors = []
        
        keywords = ['TARİH', 'FİRMA', 'HASIR', 'TİP', 'MİKTAR', 'AĞIRLIK']
        header_idx = self._find_header_row(df, keywords)
        if header_idx == -1:
            pass
        else:
            if header_idx is None: header_idx = 0
                
            df = df.iloc[header_idx:].reset_index(drop=True)
            df.columns = df.iloc[0]
            df = df.iloc[1:].reset_index(drop=True)
        self._clean_column_names(df)
        
        col_map = {}
        col_map['date'] = self._find_col(df, [r'TAR[İI]H', r'DATE'])
        col_map['supplier'] = self._find_col(df, [r'F[İI]RMA', r'TEDAR[İI]K'])
        col_map['waybill_no'] = self._find_col(df, [r'[İI]RSAL[İI]YE', r'F[İI][ŞS]'])
        col_map['mesh_type'] = self._find_col(df, [r'HASIR', 'T[İI]P', 'C[İI]NS'])
        col_map['piece_count'] = self._find_col(df, [r'ADET', 'M[İI]KTAR'])
        col_map['weight_kg'] = self._find_col(df, [r'AĞIRLIK', 'KG'])
        col_map['dimensions'] = self._find_col(df, [r'EBAT'])
        col_map['usage_location'] = self._find_col(df, [r'KULLANIM', 'YER'])
        col_map['notes'] = self._find_col(df, [r'NOT', 'AÇIKLAMA'])
        
        if not col_map['date']: return [], ["'Tarih' sütunu bulunamadı."]

        for index, row in df.iterrows():
            row_num = index + 2 + header_idx
            try:
                if row.dropna().empty: continue
                row_str = " ".join([str(v).upper() for v in row.values if pd.notna(v)])
                if "TOPLAM" in row_str or "GENEL" in row_str: continue

                data = {}
                data['date'] = self._parse_date(row.get(col_map['date']))
                if not data['date']: continue
                
                data['supplier'] = str(row.get(col_map['supplier'])).strip().upper() if col_map['supplier'] and pd.notna(row.get(col_map['supplier'])) else "BİLİNMEYEN"
                
                # Mesh Type
                if col_map['mesh_type'] and pd.notna(row.get(col_map['mesh_type'])):
                    raw_type = str(row.get(col_map['mesh_type'])).strip().upper()
                    if raw_type.startswith('Q'): data['mesh_type'] = 'Q'
                    elif raw_type.startswith('R'): data['mesh_type'] = 'R'
                    elif raw_type.startswith('T'): data['mesh_type'] = 'TR'
                    else: data['mesh_type'] = 'Q' # Default
                    
                    # Store original type in notes if specific
                    if raw_type not in ['Q', 'R', 'TR']:
                        extra_note = f"Tip: {raw_type}"
                else:
                    data['mesh_type'] = 'Q'
                    extra_note = ""

                # Counts
                data['piece_count'] = int(self._parse_float(row.get(col_map['piece_count'])))
                data['weight_kg'] = self._parse_float(row.get(col_map['weight_kg']))
                
                if data['weight_kg'] <= 0 and data['piece_count'] <= 0: continue
                
                data['dimensions'] = str(row.get(col_map['dimensions'])).strip() if col_map['dimensions'] and pd.notna(row.get(col_map['dimensions'])) else None
                data['usage_location'] = str(row.get(col_map['usage_location'])).strip() if col_map['usage_location'] and pd.notna(row.get(col_map['usage_location'])) else None
                
                notes = str(row.get(col_map['notes'])).strip() if col_map['notes'] and pd.notna(row.get(col_map['notes'])) else ""
                if extra_note: notes = f"{notes} | {extra_note}".strip(" |")
                data['notes'] = notes

                # Waybill
                if col_map['waybill_no'] and pd.notna(row.get(col_map['waybill_no'])):
                    wb = str(row.get(col_map['waybill_no'])).strip().upper()
                    if wb:
                        data['waybill_no'] = wb
                    else:
                        unique_str = f"{data['date']}_{data['supplier']}_{data['mesh_type']}_{data['weight_kg']:.2f}"
                        data['waybill_no'] = f"AUTO-{hashlib.md5(unique_str.encode()).hexdigest()[:8]}"
                else:
                    unique_str = f"{data['date']}_{data['supplier']}_{data['mesh_type']}_{data['weight_kg']:.2f}"
                    data['waybill_no'] = f"AUTO-{hashlib.md5(unique_str.encode()).hexdigest()[:8]}"

                cleaned_data.append(data)
            except Exception as e:
                errors.append(f"Satır {row_num}: {str(e)}")
                
        return cleaned_data, errors
