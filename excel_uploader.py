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
        import re
        
        # --- BAŞLIK SATIRINI BULMA (Header Detection) ---
        header_row_idx = 0
        found_header = False
        
        for i in range(min(15, len(df))):
            row_values = [str(v).upper().strip() for v in df.iloc[i].tolist() if pd.notna(v)]
            keywords = ['BETON', 'TESLİM', 'MİKTAR', 'FİRMA', 'SINIF', 'CİNSİ', 'İRSALİYE']
            match_count = sum(1 for k in keywords if any(k in rv for rv in row_values))
            
            if match_count >= 2:
                header_row_idx = i
                new_header = df.iloc[i]
                df = df[i+1:].reset_index(drop=True)
                df.columns = new_header
                found_header = True
                break
                
        # --- SÜTUNLARI BULMA VE TEMİZLEME ---
        # Unnamed sütun başlıklarını temizle (Ama verileri kaybetme)
        # Sadece tamamen boş sütunları atalım
        df = df.dropna(axis=1, how='all')
        cols = [str(c).upper().strip() for c in df.columns]
        df.columns = cols

        # Yardımcı: Sütun Bul
        def find_col(keywords):
            for i, col in enumerate(df.columns):
                for kw in keywords:
                    if kw in str(col).upper():
                        return df.columns[i]
            return None

        # Sütun Eşleştirme
        date_col = find_col(['TARİH', 'TARIH', 'ZAMAN'])
        supplier_col = find_col(['FİRMA', 'TEDARİK', 'BETONCU'])
        waybill_col = find_col(['İRSALİYE', 'IRSALIYE', 'FİŞ', 'BELGE'])
        class_col = find_col(['SINIF', 'CİNS', 'BETON CİNSİ'])
        qty_col = find_col(['MİKTAR', 'METREKÜP', 'M3', 'ADET'])
        method_col = find_col(['TESLİM', 'YÖNTEM', 'POMPA'])
        block_col = find_col(['BLOK', 'YER', 'MAHAL'])
        notes_col = find_col(['AÇIKLAMA', 'NOT'])
        
        # Eksik Sütunları Telafi Etme Denemeleri
        if not date_col:
            # Tarih formatına benzeyen ilk sütunu bul
            for col in df.columns:
                sample = df[col].dropna().head(5).astype(str).tolist()
                if any(re.search(r'\d{2}[./-]\d{2}[./-]\d{4}', s) for s in sample):
                    date_col = col
                    break

        # Eğer miktar sütunu bulunamadıysa, sayısal değer içeren sütunlara bak
        # Ancak beton fiyatı ile karışabilir. "M3" veya "Miktar" yoksa riskli.

        if not (date_col and class_col):
             return [], [f"Kritik sütunlar (Tarih, Beton Sınıfı) bulunamadı. Excel başlıklarını kontrol edin."]

        valid_classes = ['C16', 'C20', 'C25', 'C30', 'C35', 'C40', 'GRO', 'ŞAP', 'KUM', 'TAS', 'TAŞ']

        for index, row in df.iterrows():
            row_num = index + 2 + (header_row_idx if found_header else 0)
            try:
                data = {}
                
                # Boş satır kontrolü
                if pd.isna(row[date_col]) and pd.isna(row[class_col]):
                    continue

                # Tarih
                try:
                    raw_date = row[date_col]
                    if pd.isna(raw_date): continue
                    
                    if isinstance(raw_date, datetime):
                         data['date'] = raw_date.strftime('%Y-%m-%d')
                    else:
                        found_date = False
                        for fmt in ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y.%m.%d']:
                            try:
                                data['date'] = pd.to_datetime(raw_date, dayfirst=True).strftime('%Y-%m-%d')
                                found_date = True
                                break
                            except:
                                continue
                        if not found_date: raise ValueError
                except:
                    raise ValueError("Tarih formatı hatalı")

                # Firma
                if supplier_col and pd.notna(row[supplier_col]):
                    data['supplier'] = str(row[supplier_col]).strip().upper()
                else:
                    data['supplier'] = "BİLİNMEYEN FİRMA"

                # İrsaliye
                if waybill_col and pd.notna(row[waybill_col]):
                    data['waybill_no'] = str(row[waybill_col]).strip()
                else:
                    # Benzersiz bir irsaliye üret (Tarih + Rastgele)
                    import random
                    data['waybill_no'] = f"AUTO-{data['date'].replace('-','')}-{random.randint(1000,9999)}"

                # Beton Sınıfı
                if class_col:
                    raw_class = str(row[class_col]).strip().upper().replace(" ", "")
                    # İçinde geçerli sınıf geçiyor mu? (Örn: "C30 HAZIR BETON" -> "C30")
                    matched_class = next((c for c in valid_classes if c in raw_class), None)
                    if matched_class:
                        data['concrete_class'] = matched_class
                    else:
                        # GROBETON -> GRO
                        if "GRO" in raw_class: data['concrete_class'] = "GRO"
                        else: data['concrete_class'] = "Diğer" # Veritabanı enum hatası vermesin
                
                # Teslimat Şekli
                if method_col:
                    d_method = str(row[method_col]).strip().upper()
                    if "POMPA" in d_method: data['delivery_method'] = "POMPALI"
                    elif "MİKSER" in d_method: data['delivery_method'] = "MİKSERLİ"
                    else: data['delivery_method'] = "MİKSERLİ" # Varsayılan
                else:
                    data['delivery_method'] = "MİKSERLİ"

                # Miktar
                if qty_col:
                    try:
                        raw_qty = str(row[qty_col])
                        clean_qty = re.sub(r'[^\d.,]', '', raw_qty)
                        if ',' in clean_qty and '.' in clean_qty:
                            clean_qty = clean_qty.replace('.', '').replace(',', '.')
                        elif ',' in clean_qty:
                             clean_qty = clean_qty.replace(',', '.')
                        
                        data['quantity_m3'] = float(clean_qty)
                    except:
                        raise ValueError("Miktar okunamadı")
                else:
                    # Miktar sütunu yoksa, belki 'MİKSERLİ' sütununun yanında bir sütun vardır?
                    # Bu dosya formatında miktar sütunu yok gibi görünüyor veya adı 'Unnamed'.
                    # Geçici olarak 0 veya tahmin? Hata vermek en iyisi.
                    raise ValueError("Miktar sütunu bulunamadı")

                if data['quantity_m3'] <= 0: raise ValueError("Miktar 0 olamaz")

                data['location_block'] = str(row[block_col]) if block_col and pd.notna(row[block_col]) else None
                data['notes'] = str(row[notes_col]) if notes_col and pd.notna(row[notes_col]) else None

                cleaned_data.append(data)

            except Exception as e:
                errors.append(f"Satır {row_num}: {str(e)}")

        return cleaned_data, errors

    def validate_rebar(self, df):
        cleaned_data = []
        errors = []
        
        # Regex modülü
        import re
        
        # --- BAŞLIK SATIRINI BULMA (Header Detection) ---
        # Excel'in ilk 10 satırına bakıp içinde "Tarih" ve "Firma" geçen satırı başlık kabul edelim
        header_row_idx = 0
        found_header = False
        
        # İlk 15 satırı kontrol et
        for i in range(min(15, len(df))):
            # Satırdaki değerleri string'e çevirip birleştir, içinde anahtar kelimeler var mı bak
            row_values = [str(v).upper().strip() for v in df.iloc[i].tolist() if pd.notna(v)]
            
            # Anahtar kelimelerden en az 2'si varsa bu başlık satırıdır
            keywords = ['TARİH', 'FİRMA', 'TEDARİK', 'İRSALİYE', 'IRSALIYE', 'ETAP', 'AÇIKLAMA', 'NOT']
            match_count = sum(1 for k in keywords if any(k in rv for rv in row_values))
            
            if match_count >= 2:
                header_row_idx = i
                
                # Düzeltme: Dosyayı tekrar okumak yerine mevcut DataFrame'i kullan
                # i. satırı başlık yap, i+1'den sonrasını veri olarak al
                new_header = df.iloc[i]
                df = df[i+1:].reset_index(drop=True)
                df.columns = new_header
                found_header = True
                break
        
        if not found_header:
             # Bulamazsa varsayılan ilk satırı kullanır
             pass
             
        # --- SÜTUNLARI BULMA VE TEMİZLEME ---
        # Unnamed sütunları temizle ve boşlukları al
        df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]
        cols = [str(c).upper().strip() for c in df.columns]
        df.columns = cols # Temizlenmiş başlıkları geri yükle

        # Yardımcı: Bir kelime içeren sütun ismini bul
        def find_col(keywords):
            for i, col in enumerate(df.columns):
                for kw in keywords:
                    if kw in str(col).upper():
                        return df.columns[i]
            return None

        supplier_col = find_col(['TEDARİK', 'FİRMA', 'FİRMASI', 'CARİ', 'UNVAN'])
        waybill_col = find_col(['İRSALİYE', 'IRSALIYE', 'FİŞ', 'BELGE'])
        date_col = find_col(['TARİH', 'TARIH', 'ZAMAN'])

        # Demir dosyasında Firma/Tedarikçi sütunu yoksa, İrsaliye'den önceki veya sonraki sütun olabilir mi?
        # Veya görseldeki gibi sadece tarih, etap, irsaliye var, firma sütunu unutulmuş olabilir mi?
        # Eğer Firma yoksa "BİLİNMEYEN" olarak devam edelim, kullanıcıya hata verdirmeyelim (Geçici Çözüm)
        if not supplier_col:
            # Belki sütun adı boştur? İlk string içeren sütunu firma sayabiliriz ama riskli.
            pass

        if not (waybill_col and date_col):
             missing = []
             if not waybill_col: missing.append("İrsaliye No")
             if not date_col: missing.append("Tarih")
             return [], [f"Kritik sütunlar bulunamadı: {', '.join(missing)}. Excel başlık satırını kontrol edin (Tarih, İrsaliye)."]

        # Esnek Sütun Eşleştirme (Çap numarasını yakalamak için)
        def find_columns_by_diameter(columns, diameter):
            matches = []
            pattern = re.compile(rf"(^|\s|Q){diameter}(\s|'|’|l[ıi]k|l[uü]k|$)", re.IGNORECASE)
            for col in columns:
                if pattern.search(str(col)):
                    matches.append(col)
            return matches

        for index, row in df.iterrows():
            row_num = index + 2 + (header_row_idx if found_header else 0) # Gerçek Excel satır no
            try:
                data = {}
                
                # Boş satır kontrolü (Tüm ana alanlar boşsa atla)
                if pd.isna(row[date_col]) and pd.isna(row[supplier_col]):
                    continue

                # Tarih
                try:
                    raw_date = row[date_col]
                    if pd.isna(raw_date) or str(raw_date).strip() == '':
                        continue # Tarih yoksa satırı atla

                    if isinstance(raw_date, datetime):
                         data['date'] = raw_date.strftime('%Y-%m-%d')
                    else:
                        # Farklı formatları dene
                        found_date = False
                        for fmt in ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y.%m.%d']:
                            try:
                                data['date'] = pd.to_datetime(raw_date, dayfirst=True).strftime('%Y-%m-%d')
                                found_date = True
                                break
                            except:
                                continue
                        if not found_date: raise ValueError
                except:
                    raise ValueError(f"Tarih formatı hatalı: {row[date_col]}")

                # Firma & İrsaliye
                if supplier_col:
                    data['supplier'] = str(row[supplier_col]).strip().upper()
                else:
                    data['supplier'] = "BİLİNMEYEN TEDARİKÇİ" # Firma sütunu yoksa
                
                # İrsaliye boşsa "BELİRTİLMEDİ" yaz veya hata ver (tercihe göre)
                # Mevcut veritabanı yapısında NOT NULL olduğu için hata vermeli veya doldurmalı
                if pd.isna(row[waybill_col]) or str(row[waybill_col]).strip() == '':
                     # Geçici çözüm: Tarih + Firma kombinasyonu yap
                     data['waybill_no'] = f"AUTO-{data['date'].replace('-','')}"
                else:
                    data['waybill_no'] = str(row[waybill_col]).strip()
                
                # Etap
                stage_col = find_col(['ETAP', 'BÖLÜM', 'BLOK'])
                data['project_stage'] = str(row[stage_col]) if stage_col and pd.notna(row[stage_col]) else None
                
                # Notlar
                note_col = find_col(['NOT', 'AÇIKLAMA', 'ACIKLAMA'])
                notes = str(row[note_col]) if note_col and pd.notna(row[note_col]) else ""

                # Ağırlıklar
                total_weight = 0
                diameters = [8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]
                
                for d in diameters:
                    target_cols = find_columns_by_diameter(df.columns, d)
                    
                    # 24'lük Özel Durumu
                    if d == 25:
                        cols_24 = find_columns_by_diameter(df.columns, 24)
                        target_cols.extend(cols_24)
                        if cols_24:
                            val_24 = sum(float(str(row[c]).replace('.', '').replace(',', '.')) for c in cols_24 if pd.notna(row[c]))
                            if val_24 > 0:
                                notes += f" | {val_24:.0f}kg Q24 dahil"

                    val = 0.0
                    for col_name in target_cols:
                        if pd.notna(row[col_name]):
                            try:
                                raw_val = str(row[col_name])
                                # Sadece sayısal karakterleri ve virgül/noktayı al
                                # Temizleme: harfleri at
                                clean_str = re.sub(r'[^\d.,]', '', raw_val)
                                if not clean_str: continue
                                
                                # 1.250,50 -> 1250.50 dönüşümü
                                if ',' in clean_str and '.' in clean_str:
                                    if clean_str.find('.') < clean_str.find(','):
                                         # 1.250,50 (TR format)
                                         clean_str = clean_str.replace('.', '').replace(',', '.')
                                    else:
                                         # 1,250.50 (US format)
                                         clean_str = clean_str.replace(',', '')
                                elif ',' in clean_str:
                                    clean_str = clean_str.replace(',', '.')
                                
                                val += float(clean_str)
                            except:
                                pass
                    
                    data[f'q{d}_kg'] = val
                    total_weight += val

                if total_weight < 1:
                    if "TOPLAM" in str(data['supplier']): continue
                    # Eğer satırda veri yoksa ama tarih varsa, belki hatalı giriş değil boş satırdır
                    # Yine de kayıt oluşturmayalım
                    continue
                
                data['total_weight_kg'] = total_weight
                data['notes'] = notes.strip()
                if data['notes'].startswith('|'): data['notes'] = data['notes'][1:].strip()

                cleaned_data.append(data)

            except Exception as e:
                if "TOPLAM" in str(row.values): continue
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

