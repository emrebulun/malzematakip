# Şantiye Malzeme Yönetim Sistemi

## Kurulum

Bu proje Python ile geliştirilmiş bir Streamlit uygulamasıdır.

### Gereksinimler

- Python 3.10, 3.11 veya 3.12 önerilir. (Python 3.14 kullanıyorsanız bazı kütüphaneler uyarı verebilir).

### Kurulum Adımları

1. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
   *Not: Eğer kurulum sırasında hata alırsanız, eksik kütüphaneleri şu komutla tamamlayabilirsiniz:*
   ```bash
   pip install tornado gitpython pydeck tenacity toml watchdog openpyxl
   ```

2. Uygulamayı başlatın:
   ```bash
   streamlit run app.py
   ```

## Özellikler

- **Genel Bakış:** Toplam malzeme miktarları ve grafikler.
- **Beton Takibi:** İrsaliye, miktar, blok ve açıklama takibi.
- **Demir Takibi:** Çaplara göre (Q8-Q32) ağırlık hesaplama ve takip.
- **Hasır Takibi:** Tip ve ebatlara göre takip.
- **Excel İndirme:** Girilen verileri Excel formatında indirme imkanı.

