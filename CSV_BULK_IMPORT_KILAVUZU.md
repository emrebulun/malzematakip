# 🏗️ CSV Toplu Yükleme Kılavuzu

## Sorun
Supabase REST API'si varsayılan olarak **1000 kayıt limiti** ile çalışıyor. Bu yüzden 1000'den fazla beton kaydınız varsa, hepsi görünmüyor.

## ✅ Çözüm
Bu kılavuz ile **TÜM VERİLERİ** Supabase'e toplu olarak yükleyebilirsiniz.

---

## 📋 Adım 1: Excel Dosyanızı CSV'ye Dönüştürün

Excel dosyanızı CSV formatına çevirmeniz gerekiyor.

### Yöntem A: Python Script ile (Önerilen)

```bash
python excel_to_csv_converter.py C:\Users\emreb\Desktop\BETON-997.xlsx
```

Bu komut `BETON-997_converted.csv` dosyasını oluşturacak.

**Özel çıktı adı ile:**
```bash
python excel_to_csv_converter.py C:\Users\emreb\Desktop\BETON-997.xlsx beton_tum_veri.csv
```

**Belirli sheet seçmek için:**
```bash
python excel_to_csv_converter.py C:\Users\emreb\Desktop\BETON-997.xlsx beton_data.csv Sayfa1
```

### Yöntem B: Excel'de Manuel

1. Excel dosyasını açın
2. **File → Save As** 
3. **Save as type**: CSV (Comma delimited) (*.csv)
4. Dosyayı kaydedin

---

## 📋 Adım 2: Supabase Bağlantı Bilgilerini Ayarlayın

`.streamlit/secrets.toml` dosyanızın olduğundan emin olun:

```toml
[supabase]
url = "https://your-project.supabase.co"
anon_key = "your-anon-key-here"
```

**Eğer yoksa:**

1. Projenizin kök dizininde `.streamlit` klasörü oluşturun
2. İçine `secrets.toml` dosyası oluşturun
3. Yukarıdaki içeriği yapıştırın ve kendi bilgilerinizi girin

---

## 📋 Adım 3: CSV Verilerini Toplu Yükleme

Şimdi CSV dosyanızı Supabase'e yükleyin:

```bash
python bulk_import_csv_to_supabase.py beton_tum_veri.csv
```

veya dönüştürülen dosyayı kullanın:

```bash
python bulk_import_csv_to_supabase.py BETON-997_converted.csv
```

### Script Ne Yapar?

1. ✅ CSV dosyasını okur
2. ✅ Verileri Supabase formatına dönüştürür
3. ✅ **500'lük batchler** halinde yükler (API limiti sorunu yok!)
4. ✅ İrsaliye numarasına göre firmaları otomatik düzeltir (>14000 = ALBAYRAK, ≤14000 = ÖZYURT)
5. ✅ Progress gösterir
6. ✅ Başarılı ve başarısız kayıt sayısını raporlar

---

## 📊 Örnek Kullanım

```bash
# 1. Excel'i CSV'ye çevir
python excel_to_csv_converter.py C:\Users\emreb\Desktop\BETON-997.xlsx

# 2. CSV'yi Supabase'e yükle
python bulk_import_csv_to_supabase.py BETON-997_converted.csv
```

### Çıktı Örneği:

```
==================================================
🏗️  CSV TO SUPABASE BULK IMPORT
==================================================

📄 CSV Dosyası: BETON-997_converted.csv
📊 Hedef Tablo: concrete_logs

🔌 Supabase'e bağlanılıyor...
✅ Bağlantı başarılı!

📖 CSV dosyası okunuyor...
✅ 9542 satır okundu

⚙️ Veriler hazırlanıyor...
✅ 9542 kayıt hazır

❓ 9542 kayıt Supabase'e eklenecek. Devam? (evet/hayir): evet

🚀 Toplu yükleme başlıyor...

📦 Batch 1/20 işleniyor... (500 kayıt)
   ✅ 500 kayıt başarıyla eklendi

📦 Batch 2/20 işleniyor... (500 kayıt)
   ✅ 500 kayıt başarıyla eklendi

...

📦 Batch 20/20 işleniyor... (42 kayıt)
   ✅ 42 kayıt başarıyla eklendi

==================================================
🎉 İşlem tamamlandı!
✅ Başarılı: 9542 kayıt
❌ Başarısız: 0 kayıt
📊 Toplam: 9542 kayıt
==================================================
```

---

## 🔄 Adım 4: Uygulamayı Yeniden Başlatın

Streamlit uygulamanızı yenileyin veya yeniden başlatın:

```bash
streamlit run app.py
```

Artık **TÜM VERİLERİNİZ** görünecek! 🎉

---

## 🐛 Sorun Giderme

### "Supabase bilgileri bulunamadı" hatası

**Çözüm:** `.streamlit/secrets.toml` dosyasını oluşturun ve Supabase bilgilerinizi ekleyin.

### "CSV dosyası bulunamadı" hatası

**Çözüm:** Dosya yolunu tam olarak yazın:
```bash
python bulk_import_csv_to_supabase.py "C:\Users\emreb\Desktop\beton_data.csv"
```

### Bazı kayıtlar yüklenmiyor

**Çözüm:** 
- CSV'de gerekli kolonların olduğundan emin olun: `TARİH`, `MİKTAR`, `BETON SINIFI` vs.
- Tarih formatının düzgün olduğundan emin olun
- Miktar değerinin sayısal olduğundan emin olun

### Duplicate (tekrarlanan) kayıtlar

Eğer daha önce yükleme yaptıysanız ve tekrar yüklüyorsanız, duplicate kayıtlar oluşabilir.

**Çözüm:** Supabase dashboard'da tabloyu temizleyin veya unique constraint ekleyin.

---

## 📈 Pagination Düzeltmesi

Ayrıca `db_manager_rest.py` dosyasında **pagination (sayfalama)** ekledik. Bu sayede:

- ✅ `get_concrete_logs()` artık TÜM kayıtları çeker (1000 değil!)
- ✅ `get_rebar_logs()` artık TÜM kayıtları çeker
- ✅ `get_mesh_logs()` artık TÜM kayıtları çeker
- ✅ Tüm summary ve analytics fonksiyonları TÜM verileri kullanır

**Uygulama otomatik olarak güncellenecek.** Sadece yenileyin!

---

## 🎯 Özet

1. ✅ Excel → CSV dönüştürme scripti
2. ✅ CSV → Supabase toplu yükleme scripti
3. ✅ Pagination düzeltmesi (1000 limit sorunu çözüldü)
4. ✅ Batch insert (500'lük gruplar halinde güvenli yükleme)
5. ✅ Otomatik firma düzeltmesi

---

## 💡 İpuçları

- **Büyük dosyalar için:** Script otomatik olarak batch'ler halinde yükler, sabırlı olun
- **Backup alın:** Supabase'e yüklemeden önce verilerinizin yedeğini alın
- **Test edin:** İlk olarak küçük bir CSV ile test edin (örn: ilk 100 satır)

---

## 📞 Destek

Sorun yaşarsanız:
1. Script'in çıktısını kontrol edin
2. Supabase dashboard'u kontrol edin
3. `.streamlit/secrets.toml` dosyasını kontrol edin

**Başarılar!** 🚀

