import pandas as pd
import numpy as np
from datetime import datetime

class ExcelValidator:
    def __init__(self):
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
            'Q8': 'q8_kg', 'Q10': 'q10_kg', 'Q12': 'q12_kg', 'Q14': 'q14_kg',
            'Q16': 'q16_kg', 'Q18': 'q18_kg', 'Q20': 'q20_kg', 'Q22': 'q22_kg',
            'Q25': 'q25_kg', 'Q28': 'q28_kg', 'Q32': 'q32_kg',
            'Notlar': 'notes'
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

    def validate_concrete(self, df):
        cleaned_data = []
        errors = []
        
        # Sütun kontrolü
        missing_cols = [col for col in self.concrete_columns.keys() if col not in df.columns]
        if missing_cols:
            return [], [f"Eksik Sütunlar: {', '.join(missing_cols)}"]

        valid_classes = ['C16', 'C20', 'C25', 'C30', 'C35', 'C40', 'GRO', 'ŞAP']
        valid_delivery = ['POMPALI', 'MİKSERLİ']

        for index, row in df.iterrows():
            row_num = index + 2
            try:
                # Temel Dönüşümler
                data = {}
                
                # Tarih
                try:
                    data['date'] = pd.to_datetime(row['Tarih']).strftime('%Y-%m-%d')
                except:
                    raise ValueError("Tarih formatı hatalı (Beklenen: GG.AA.YYYY)")

                # Zorunlu Alanlar
                if pd.isna(row['Firma']) or str(row['Firma']).strip() == '':
                    raise ValueError("Firma adı boş olamaz")
                data['supplier'] = str(row['Firma']).strip().upper()

                if pd.isna(row['İrsaliye No']) or str(row['İrsaliye No']).strip() == '':
                    raise ValueError("İrsaliye No boş olamaz")
                data['waybill_no'] = str(row['İrsaliye No']).strip()

                # Beton Sınıfı
                c_class = str(row['Beton Sınıfı']).strip().upper().replace(" ", "")
                if c_class not in valid_classes:
                    raise ValueError(f"Geçersiz Beton Sınıfı: {row['Beton Sınıfı']} (Geçerli: {', '.join(valid_classes)})")
                data['concrete_class'] = c_class

                # Teslimat Şekli
                d_method = str(row['Teslimat Şekli']).strip().upper()
                # Varsayılan değer atama veya düzeltme
                if "POMPA" in d_method: d_method = "POMPALI"
                elif "MİKSER" in d_method: d_method = "MİKSERLİ"
                
                if d_method not in valid_delivery:
                    raise ValueError(f"Geçersiz Teslimat Şekli: {row['Teslimat Şekli']}")
                data['delivery_method'] = d_method

                # Miktar
                try:
                    qty = float(str(row['Miktar']).replace(',', '.'))
                    if qty <= 0: raise ValueError
                    data['quantity_m3'] = qty
                except:
                    raise ValueError(f"Geçersiz Miktar: {row['Miktar']}")

                # Opsiyonel Alanlar
                data['location_block'] = str(row['Blok']) if pd.notna(row['Blok']) else None
                data['notes'] = str(row['Açıklama']) if pd.notna(row['Açıklama']) else None

                cleaned_data.append(data)

            except Exception as e:
                errors.append(f"Satır {row_num}: {str(e)}")

        return cleaned_data, errors

    def validate_rebar(self, df):
        cleaned_data = []
        errors = []
        
        # Sütun kontrolü (Q çapları hariç temel sütunlar)
        base_cols = ['Tarih', 'Tedarikçi', 'İrsaliye No']
        missing_cols = [col for col in base_cols if col not in df.columns]
        if missing_cols:
            return [], [f"Eksik Sütunlar: {', '.join(missing_cols)}"]

        for index, row in df.iterrows():
            row_num = index + 2
            try:
                data = {}
                
                # Tarih
                try:
                    data['date'] = pd.to_datetime(row['Tarih']).strftime('%Y-%m-%d')
                except:
                    raise ValueError("Tarih formatı hatalı")

                # Zorunlu Alanlar
                if pd.isna(row['Tedarikçi']) or str(row['Tedarikçi']).strip() == '':
                    raise ValueError("Tedarikçi boş olamaz")
                data['supplier'] = str(row['Tedarikçi']).strip().upper()

                if pd.isna(row['İrsaliye No']) or str(row['İrsaliye No']).strip() == '':
                    raise ValueError("İrsaliye No boş olamaz")
                data['waybill_no'] = str(row['İrsaliye No']).strip()

                # Opsiyonel Stringler
                data['project_stage'] = str(row['Etap']) if pd.notna(row['Etap']) else None
                data['manufacturer'] = str(row['Üretici']) if pd.notna(row['Üretici']) else None
                data['notes'] = str(row.get('Notlar', '')) if pd.notna(row.get('Notlar')) else None

                # Ağırlıklar
                total_weight = 0
                diameters = [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]
                
                for d in diameters:
                    col_name = f'Q{d}'
                    key_name = f'q{d}_kg'
                    val = 0.0
                    if col_name in df.columns and pd.notna(row[col_name]):
                        try:
                            val = float(str(row[col_name]).replace(',', '.'))
                        except:
                            raise ValueError(f"{col_name} değeri sayısal değil")
                    data[key_name] = val
                    total_weight += val

                if total_weight <= 0:
                    raise ValueError("Toplam ağırlık 0 olamaz. En az bir çap girilmelidir.")
                
                data['total_weight_kg'] = total_weight
                cleaned_data.append(data)

            except Exception as e:
                errors.append(f"Satır {row_num}: {str(e)}")

        return cleaned_data, errors

    def validate_mesh(self, df):
        cleaned_data = []
        errors = []
        
        missing_cols = [col for col in ['Tarih', 'Firma', 'İrsaliye No', 'Hasır Tipi', 'Adet', 'Ağırlık'] if col not in df.columns]
        if missing_cols:
            return [], [f"Eksik Sütunlar: {', '.join(missing_cols)}"]

        valid_types = ['Q', 'R', 'TR'] # Basitleştirilmiş kontrol, DB enum'a göre
        # Not: DB'de enum Q, R, TR olarak tanımlı ama uygulamada Q131, Q188 vb kullanılıyor.
        # Burada sadece prefix kontrolü yapabiliriz veya uygulamadaki gibi serbest bırakıp DB enum'una uygun hale getirebiliriz.
        # Schema: mesh_type_enum ('Q', 'R', 'TR') -> Bu enum biraz dar, uygulamada Q131 vb var. 
        # DB şemasına tekrar baktığımda: CREATE TYPE mesh_type_enum AS ENUM ('Q', 'R', 'TR');
        # Ancak uygulama kodunda "Q131" gibi değerler var. Muhtemelen DB'ye yazarken sadece ilk harfi veya Q/R tipini almalı.
        # Veya DB enum'ı güncellenmeli. Şimdilik güvenli olması için sadece Q, R veya TR olarak map edelim.
        
        for index, row in df.iterrows():
            row_num = index + 2
            try:
                data = {}
                
                try:
                    data['date'] = pd.to_datetime(row['Tarih']).strftime('%Y-%m-%d')
                except:
                    raise ValueError("Tarih formatı hatalı")

                data['supplier'] = str(row['Firma']).strip().upper()
                data['waybill_no'] = str(row['İrsaliye No']).strip()
                
                # Mesh Type Mapping
                raw_type = str(row['Hasır Tipi']).strip().upper()
                if raw_type.startswith('Q'): data['mesh_type'] = 'Q'
                elif raw_type.startswith('R'): data['mesh_type'] = 'R'
                elif raw_type.startswith('T'): data['mesh_type'] = 'TR'
                else:
                    # Default or Error? Let's try to handle broadly or fail
                    # DB constraint might fail if not mapped.
                    # Let's assume Q for unknown for now or raise error
                    raise ValueError(f"Bilinmeyen Hasır Tipi: {raw_type} (Q, R veya TR ile başlamalı)")

                # Store full type info in notes if needed or dimensions
                # But schema has specific columns. 
                # Let's stick to schema: mesh_type (ENUM), dimensions (TEXT)
                
                data['dimensions'] = str(row['Ebatlar']) if pd.notna(row['Ebatlar']) else None
                
                try:
                    data['piece_count'] = int(row['Adet'])
                    data['weight_kg'] = float(str(row['Ağırlık']).replace(',', '.'))
                except:
                    raise ValueError("Adet veya Ağırlık sayısal olmalı")

                data['usage_location'] = str(row['Kullanım Yeri']) if pd.notna(row['Kullanım Yeri']) else None
                data['notes'] = str(row.get('Notlar', '')) if pd.notna(row.get('Notlar')) else None
                
                # Append original type info to notes if specific type like Q131 is used
                if raw_type not in ['Q', 'R', 'TR']:
                    if data['notes']: data['notes'] += f" - Tip: {raw_type}"
                    else: data['notes'] = f"Tip: {raw_type}"

                cleaned_data.append(data)

            except Exception as e:
                errors.append(f"Satır {row_num}: {str(e)}")

        return cleaned_data, errors

