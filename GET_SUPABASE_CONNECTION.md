# 🔌 Supabase Bağlantı Bilgilerini Alma Rehberi

## ⚠️ ŞU AN SORUN: Connection Timeout

Bilgisayarınız Supabase'e bağlanamıyor. **Doğru connection string'i** almanız gerekiyor.

---

## 📋 Adım 1: Supabase Dashboard'a Gidin

1. **Tarayıcınızda açın:** https://supabase.com/dashboard
2. **Projenizi seçin:** `xmlnpyrgxlvyzphzqeug` (sizin proje)
3. Sol menüden **Settings** > **Database** tıklayın

---

## 📋 Adım 2: Connection String'i Kopyalayın

**"Connection string"** bölümünde **3 farklı mod** göreceksiniz:

### ✅ Mod 1: **Transaction** (Önerilen - Port 6543)
```
postgresql://postgres.xmlnpyrgxlvyzphzqeug:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```
- ✅ **En stabil** - Firewall sorunları daha az
- ✅ Connection pooling var
- ✅ **ÖNCELİKLE BUNU DENEYİN**

### Mod 2: **Session** (Port 6543)
```
postgresql://postgres.xmlnpyrgxlvyzphzqeug:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres?pgbouncer=true
```

### Mod 3: **Direct** (Port 5432)
```
postgresql://postgres:[YOUR-PASSWORD]@db.xmlnpyrgxlvyzphzqeug.supabase.co:5432/postgres
```
- ❌ **Şu an çalışmıyor** (connection timeout)

---

## 📋 Adım 3: Doğru Connection String'i Buraya Yapıştırın

1. Yukarıdaki **Transaction** connection string'ini kopyalayın
2. `[YOUR-PASSWORD]` yerine şifrenizi yazın: `05344274465.Eb`
3. Bana buraya yapıştırın (tam haliyle)

**Örnek:**
```
postgresql://postgres.xmlnpyrgxlvyzphzqeug:05344274465.Eb@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

---

## 🔍 Alternatif: Supabase REST API Kullanımı

Eğer PostgreSQL direkt bağlantısı hiç çalışmazsa, **Supabase REST API** ile de çalışabiliriz:

1. **Settings** > **API** gidin
2. **Project URL** ve **anon key** kopyalayın
3. Python'da `supabase-py` kütüphanesi ile bağlanırız (daha kolay)

---

## ✅ Yapmanız Gereken:

**ŞİMDİ:** Supabase Dashboard'dan **Transaction mode** connection string'ini alın ve bana gönderin!

Örnek format:
```
postgresql://postgres.xmlnpyrgxlvyzphzqeug:05344274465.Eb@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

(Sizinki farklı bir region'da olabilir: `aws-0-us-east-1` gibi)


