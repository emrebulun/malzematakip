import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, engine, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database
TEST_DATABASE_URL = "sqlite:///./test_santiye.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_create_beton():
    beton_data = {
        "tarih": "2025-11-20T10:00:00",
        "firma": "ÖZYURT BETON",
        "irsaliye_no": "12345",
        "beton_sinifi": "C25",
        "teslim_sekli": "POMPALI",
        "miktar": 25.5,
        "blok": "GK1",
        "aciklama": "Test"
    }
    response = client.post("/api/beton/", json=beton_data)
    assert response.status_code == 200
    data = response.json()
    assert data["miktar"] == 25.5
    assert data["beton_sinifi"] == "C25"

def test_get_all_beton():
    response = client.get("/api/beton/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_demir():
    demir_data = {
        "tarih": "2025-11-20T10:00:00",
        "etap": "3.ETAP",
        "irsaliye_no": "5678",
        "tedarikci": "ŞAHİN DEMİR",
        "uretici": "KARDEMİR",
        "q8": 0,
        "q10": 1000,
        "q12": 2000,
        "q14": 0,
        "q16": 3000,
        "q18": 0,
        "q20": 0,
        "q22": 0,
        "q25": 0,
        "q28": 0,
        "q32": 0,
        "toplam_agirlik": 6000
    }
    response = client.post("/api/demir/", json=demir_data)
    assert response.status_code == 200
    data = response.json()
    assert data["toplam_agirlik"] == 6000

def test_dashboard_analytics():
    response = client.get("/api/analytics/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "toplam_beton" in data
    assert "toplam_demir" in data
    assert "toplam_hasir" in data

def test_summary_stats():
    response = client.get("/api/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_records" in data
    assert "total_quantities" in data



