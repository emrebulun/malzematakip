# Şantiye Malzeme Yönetim Sistemi - Backend API

## Kurulum

### 1. Backend Bağımlılıklarını Yükleyin

```bash
pip install -r backend_requirements.txt
```

### 2. Veritabanını Başlatın

API ilk çalıştırıldığında otomatik olarak `santiye_997.db` SQLite veritabanı oluşturulur.

### 3. API Sunucusunu Başlatın

```bash
python main.py
```

API şu adreste çalışmaya başlayacak: `http://localhost:8000`

### 4. API Dokümantasyonunu Görüntüleyin

Tarayıcınızda şu adreslere gidin:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Beton (Concrete)

- `POST /api/beton/` - Yeni beton kaydı ekle
- `GET /api/beton/` - Tüm beton kayıtlarını listele
- `GET /api/beton/{id}` - Belirli bir beton kaydını getir
- `DELETE /api/beton/{id}` - Beton kaydını sil

### Demir (Rebar/Iron)

- `POST /api/demir/` - Yeni demir kaydı ekle
- `GET /api/demir/` - Tüm demir kayıtlarını listele
- `GET /api/demir/{id}` - Belirli bir demir kaydını getir
- `DELETE /api/demir/{id}` - Demir kaydını sil

### Hasır (Mesh)

- `POST /api/hasir/` - Yeni hasır kaydı ekle
- `GET /api/hasir/` - Tüm hasır kayıtlarını listele
- `GET /api/hasir/{id}` - Belirli bir hasır kaydını getir
- `DELETE /api/hasir/{id}` - Hasır kaydını sil

### Analytics

- `GET /api/analytics/dashboard` - Tüm malzemelerin analiz verilerini getir

### Excel Import

- `POST /api/import/beton` - Excel dosyasından beton kayıtlarını içe aktar

## Örnek Kullanım

### Python ile API Çağrısı

```python
import requests

# Yeni beton kaydı ekleme
data = {
    "tarih": "2025-11-20T10:00:00",
    "firma": "ÖZYURT BETON",
    "irsaliye_no": "12345",
    "beton_sinifi": "C25",
    "teslim_sekli": "POMPALI",
    "miktar": 25.5,
    "blok": "GK1",
    "aciklama": "2.Kat Tabliye"
}

response = requests.post("http://localhost:8000/api/beton/", json=data)
print(response.json())

# Dashboard verilerini alma
response = requests.get("http://localhost:8000/api/analytics/dashboard")
print(response.json())
```

### cURL ile API Çağrısı

```bash
# Dashboard verilerini getir
curl http://localhost:8000/api/analytics/dashboard

# Tüm beton kayıtlarını listele
curl http://localhost:8000/api/beton/
```

## Veritabanı Yapısı

### Beton Tablosu
- id (Primary Key)
- tarih
- firma
- irsaliye_no
- beton_sinifi
- teslim_sekli
- miktar (m³)
- blok
- aciklama
- created_at

### Demir Tablosu
- id (Primary Key)
- tarih
- etap
- irsaliye_no
- tedarikci
- uretici
- q8, q10, q12, q14, q16, q18, q20, q22, q25, q28, q32 (kg)
- toplam_agirlik (kg)
- created_at

### Hasır Tablosu
- id (Primary Key)
- tarih
- firma
- irsaliye_no
- etap
- hasir_tipi
- ebatlar
- adet
- agirlik (kg)
- kullanim_yeri
- created_at

## Özellikler

- ✅ RESTful API yapısı
- ✅ SQLite veritabanı
- ✅ Otomatik API dokümantasyonu (Swagger/ReDoc)
- ✅ CORS desteği
- ✅ Excel dosyası import
- ✅ Analytics endpoints
- ✅ Otomatik firma belirleme (İrsaliye no > 14000 = Albayrak, ≤ 14000 = Özyurt)

## Production Notları

Production ortamında kullanım için:
1. SQLite yerine PostgreSQL/MySQL kullanın
2. Çevre değişkenleri ile yapılandırma yapın
3. Authentication/Authorization ekleyin
4. Rate limiting uygulayın
5. HTTPS kullanın



