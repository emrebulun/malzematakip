# 🔧 Supabase SQL Düzeltme Talimatları

## Sorun:
Beton tablosunda **unique constraint** var, bu yüzden sadece 1,000 kayıt yükleniyor.

## ✅ ÇÖZÜM: Constraint'i Kaldır

### 1️⃣ Supabase Dashboard'a Git:
```
https://supabase.com/dashboard/project/xmlnpyrgxlvyzphzqeug
```

### 2️⃣ Sol Menüden "SQL Editor" Tıkla

### 3️⃣ Bu Komutu Yapıştır ve Çalıştır:

```sql
-- Unique constraint'i kaldır
ALTER TABLE concrete_logs 
DROP CONSTRAINT IF EXISTS unique_concrete_waybill;

-- Verify (kontrol)
SELECT COUNT(*) FROM concrete_logs;
```

### 4️⃣ Sonucu Buradan Kontrol Et
Komut başarılı olursa "Success" göreceksin.

---

## Alternatif: Manuel CSV Import

Eğer SQL çalışmazsa:

1. `concrete_import.csv` dosyasını Supabase'e manuel yükle
2. Dashboard > Table Editor > concrete_logs > Insert > Import CSV
3. Dosyayı seç ve import et

---

**Hangisini yapmak istersiniz?**
- SQL çalıştır (2 dakika) ✅ ÖNERİLEN
- CSV manuel import (5 dakika)



