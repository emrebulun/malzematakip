from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

# Beton (Concrete) Model
class Beton(Base):
    __tablename__ = "beton"
    
    id = Column(Integer, primary_key=True, index=True)
    tarih = Column(DateTime, default=datetime.now)
    firma = Column(String(100))
    irsaliye_no = Column(String(50))
    beton_sinifi = Column(String(50))
    teslim_sekli = Column(String(50))
    miktar = Column(Float)  # m3
    blok = Column(String(100))
    aciklama = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

# Demir (Iron/Rebar) Model
class Demir(Base):
    __tablename__ = "demir"
    
    id = Column(Integer, primary_key=True, index=True)
    tarih = Column(DateTime, default=datetime.now)
    etap = Column(String(50))
    irsaliye_no = Column(String(50))
    tedarikci = Column(String(100))
    uretici = Column(String(100))
    q8 = Column(Float, default=0)
    q10 = Column(Float, default=0)
    q12 = Column(Float, default=0)
    q14 = Column(Float, default=0)
    q16 = Column(Float, default=0)
    q18 = Column(Float, default=0)
    q20 = Column(Float, default=0)
    q22 = Column(Float, default=0)
    q25 = Column(Float, default=0)
    q28 = Column(Float, default=0)
    q32 = Column(Float, default=0)
    toplam_agirlik = Column(Float)  # kg
    created_at = Column(DateTime, default=datetime.now)

# Hasir (Mesh) Model
class Hasir(Base):
    __tablename__ = "hasir"
    
    id = Column(Integer, primary_key=True, index=True)
    tarih = Column(DateTime, default=datetime.now)
    firma = Column(String(100))
    irsaliye_no = Column(String(50))
    etap = Column(String(50))
    hasir_tipi = Column(String(50))
    ebatlar = Column(String(100))
    adet = Column(Integer)
    agirlik = Column(Float)  # kg
    kullanim_yeri = Column(String(200))
    created_at = Column(DateTime, default=datetime.now)

# Database setup
DATABASE_URL = "sqlite:///./santiye_997.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()






