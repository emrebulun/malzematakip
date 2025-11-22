# 🚀 Uygulamayı Canlıya Alma Rehberi (Streamlit Cloud)

Uygulamanızı internette herkesin erişimine açmak için aşağıdaki adımları izleyin.

---

## 1. Adım: GitHub'a Yükleme

Streamlit Cloud, kodları GitHub'dan çeker.

1. **GitHub Hesabı:** [github.com](https://github.com) adresinden hesabınız yoksa açın.
2. **Yeni Depo (Repository):**
   - Sağ üstteki `+` ikonuna tıklayın -> **New repository**.
   - İsim verin (örn: `santiye-stok-takip`).
   - **Public** seçin (Ücretsiz sürüm için).
   - "Create repository" deyin.
3. **Kodları Yükleme:**
   - Bilgisayarınızda projenin olduğu klasörde şu komutları çalıştırın (Git kurulu olmalı):
     ```bash
     git init
     git add .
     git commit -m "İlk yükleme"
     git branch -M main
     git remote add origin https://github.com/KULLANICI_ADINIZ/santiye-stok-takip.git
     git push -u origin main
     ```
   - *Not: `KULLANICI_ADINIZ` kısmını kendi GitHub kullanıcı adınızla değiştirin.*

---

## 2. Adım: Streamlit Cloud Hesabı

1. [share.streamlit.io](https://share.streamlit.io) adresine gidin.
2. "Continue with GitHub" diyerek giriş yapın.

---

## 3. Adım: Uygulamayı Oluşturma

1. Sağ üstteki **"New app"** butonuna tıklayın.
2. **"Use existing repo"** seçeneğini seçin.
3. **Repository:** `kullanici_adiniz/santiye-stok-takip` seçin.
4. **Branch:** `main` (otomatik gelir).
5. **Main file path:** `streamlit_app.py` (otomatik gelmeli, gelmezse elle yazın).
6. **Deploy!** butonuna tıklayın.

---

## 4. Adım: Şifreleri (Secrets) Ekleme 🔑 [ÇOK ÖNEMLİ]

Uygulama ilk açıldığında **Hata verecektir** çünkü Supabase şifrelerini bilmiyor.

1. Streamlit dashboard'unda uygulamanızın sağ alt köşesindeki **Settings** (Manage app) menüsüne gidin.
2. **Secrets** sekmesine tıklayın.
3. Bilgisayarınızdaki `.streamlit/secrets.toml` dosyasının içeriğini kopyalayın.
4. Oradaki kutuya yapıştırın:
   ```toml
   [supabase]
   url = "https://sizin-proje-urlniz.supabase.co"
   anon_key = "sizin-anon-keyiniz"
   ```
5. **Save** butonuna tıklayın.

---

## 🎉 Tebrikler!

Uygulamanız artık canlıda! Size `https://santiye-stok-takip.streamlit.app` gibi bir link verecek. Bu linki telefondan, tabletten veya bilgisayardan açabilirsiniz.

---

### 💡 İpuçları

- **Veriler Nerede?** Verileriniz Supabase'de durduğu için, canlı uygulamadan girdiğiniz veri anında veritabanına yazılır.
- **Güncelleme:** Kodda bir değişiklik yaparsanız (örn: yeni grafik eklerseniz), GitHub'a `git push` yaptığınız anda canlı uygulama otomatik güncellenir.

