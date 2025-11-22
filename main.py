from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager
import pandas as pd
from datetime import datetime

from database import get_db, init_db, Beton, Demir, Hasir
from schemas import (
    BetonCreate, BetonResponse, DemirCreate, DemirResponse,
    HasirCreate, HasirResponse, DashboardStats, BetonAnalytics,
    DemirAnalytics, HasirAnalytics
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (if needed)

app = FastAPI(title="Şantiye Malzeme Yönetim API", version="1.0.0", lifespan=lifespan)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check
@app.get("/")
def read_root():
    return {"message": "Şantiye Malzeme Yönetim API - Çalışıyor", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# ========== BETON ENDPOINTS ==========

@app.post("/api/beton/", response_model=BetonResponse)
def create_beton(beton: BetonCreate, db: Session = Depends(get_db)):
    db_beton = Beton(**beton.dict())
    
    # İrsaliye numarasına göre firma otomatik belirleme
    try:
        irsa_num = float(beton.irsaliye_no)
        if irsa_num > 14000:
            db_beton.firma = "ALBAYRAK BETON"
        else:
            db_beton.firma = "ÖZYURT BETON"
    except:
        pass  # İrsaliye numarası sayıya çevrilemezse, gönderilen firma değeri kullanılır
    
    db.add(db_beton)
    db.commit()
    db.refresh(db_beton)
    return db_beton

@app.get("/api/beton/", response_model=List[BetonResponse])
def get_all_beton(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    betons = db.query(Beton).offset(skip).limit(limit).all()
    return betons

@app.get("/api/beton/{beton_id}", response_model=BetonResponse)
def get_beton(beton_id: int, db: Session = Depends(get_db)):
    beton = db.query(Beton).filter(Beton.id == beton_id).first()
    if not beton:
        raise HTTPException(status_code=404, detail="Beton kaydı bulunamadı")
    return beton

@app.put("/api/beton/{beton_id}", response_model=BetonResponse)
def update_beton(beton_id: int, beton: BetonCreate, db: Session = Depends(get_db)):
    db_beton = db.query(Beton).filter(Beton.id == beton_id).first()
    if not db_beton:
        raise HTTPException(status_code=404, detail="Beton kaydı bulunamadı")
    
    for key, value in beton.dict().items():
        setattr(db_beton, key, value)
    
    # İrsaliye numarasına göre firma otomatik belirleme
    try:
        irsa_num = float(beton.irsaliye_no)
        if irsa_num > 14000:
            db_beton.firma = "ALBAYRAK BETON"
        else:
            db_beton.firma = "ÖZYURT BETON"
    except:
        pass
    
    db.commit()
    db.refresh(db_beton)
    return db_beton

@app.delete("/api/beton/{beton_id}")
def delete_beton(beton_id: int, db: Session = Depends(get_db)):
    beton = db.query(Beton).filter(Beton.id == beton_id).first()
    if not beton:
        raise HTTPException(status_code=404, detail="Beton kaydı bulunamadı")
    db.delete(beton)
    db.commit()
    return {"message": "Kayıt silindi"}

# ========== DEMİR ENDPOINTS ==========

@app.post("/api/demir/", response_model=DemirResponse)
def create_demir(demir: DemirCreate, db: Session = Depends(get_db)):
    db_demir = Demir(**demir.dict())
    db.add(db_demir)
    db.commit()
    db.refresh(db_demir)
    return db_demir

@app.get("/api/demir/", response_model=List[DemirResponse])
def get_all_demir(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    demirs = db.query(Demir).offset(skip).limit(limit).all()
    return demirs

@app.get("/api/demir/{demir_id}", response_model=DemirResponse)
def get_demir(demir_id: int, db: Session = Depends(get_db)):
    demir = db.query(Demir).filter(Demir.id == demir_id).first()
    if not demir:
        raise HTTPException(status_code=404, detail="Demir kaydı bulunamadı")
    return demir

@app.put("/api/demir/{demir_id}", response_model=DemirResponse)
def update_demir(demir_id: int, demir: DemirCreate, db: Session = Depends(get_db)):
    db_demir = db.query(Demir).filter(Demir.id == demir_id).first()
    if not db_demir:
        raise HTTPException(status_code=404, detail="Demir kaydı bulunamadı")
    
    for key, value in demir.dict().items():
        setattr(db_demir, key, value)
    
    db.commit()
    db.refresh(db_demir)
    return db_demir

@app.delete("/api/demir/{demir_id}")
def delete_demir(demir_id: int, db: Session = Depends(get_db)):
    demir = db.query(Demir).filter(Demir.id == demir_id).first()
    if not demir:
        raise HTTPException(status_code=404, detail="Demir kaydı bulunamadı")
    db.delete(demir)
    db.commit()
    return {"message": "Kayıt silindi"}

# ========== HASIR ENDPOINTS ==========

@app.post("/api/hasir/", response_model=HasirResponse)
def create_hasir(hasir: HasirCreate, db: Session = Depends(get_db)):
    db_hasir = Hasir(**hasir.dict())
    db.add(db_hasir)
    db.commit()
    db.refresh(db_hasir)
    return db_hasir

@app.get("/api/hasir/", response_model=List[HasirResponse])
def get_all_hasir(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    hasirs = db.query(Hasir).offset(skip).limit(limit).all()
    return hasirs

@app.get("/api/hasir/{hasir_id}", response_model=HasirResponse)
def get_hasir(hasir_id: int, db: Session = Depends(get_db)):
    hasir = db.query(Hasir).filter(Hasir.id == hasir_id).first()
    if not hasir:
        raise HTTPException(status_code=404, detail="Hasır kaydı bulunamadı")
    return hasir

@app.put("/api/hasir/{hasir_id}", response_model=HasirResponse)
def update_hasir(hasir_id: int, hasir: HasirCreate, db: Session = Depends(get_db)):
    db_hasir = db.query(Hasir).filter(Hasir.id == hasir_id).first()
    if not db_hasir:
        raise HTTPException(status_code=404, detail="Hasır kaydı bulunamadı")
    
    for key, value in hasir.dict().items():
        setattr(db_hasir, key, value)
    
    db.commit()
    db.refresh(db_hasir)
    return db_hasir

@app.delete("/api/hasir/{hasir_id}")
def delete_hasir(hasir_id: int, db: Session = Depends(get_db)):
    hasir = db.query(Hasir).filter(Hasir.id == hasir_id).first()
    if not hasir:
        raise HTTPException(status_code=404, detail="Hasır kaydı bulunamadı")
    db.delete(hasir)
    db.commit()
    return {"message": "Kayıt silindi"}

# ========== ANALYTICS ENDPOINTS ==========

@app.get("/api/analytics/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    # Beton Analytics
    betons = db.query(Beton).all()
    toplam_beton = sum([b.miktar for b in betons])
    
    firma_dagilimi = {}
    sinif_dagilimi = {}
    blok_dagilimi = {}
    
    for b in betons:
        firma_dagilimi[b.firma] = firma_dagilimi.get(b.firma, 0) + b.miktar
        sinif_dagilimi[b.beton_sinifi] = sinif_dagilimi.get(b.beton_sinifi, 0) + b.miktar
        blok = b.blok or "Bilinmiyor"
        blok_dagilimi[blok] = blok_dagilimi.get(blok, 0) + b.miktar
    
    beton_analytics = {
        "toplam_miktar": toplam_beton,
        "firma_dagilimi": firma_dagilimi,
        "sinif_dagilimi": sinif_dagilimi,
        "blok_dagilimi": blok_dagilimi
    }
    
    # Demir Analytics
    demirs = db.query(Demir).all()
    toplam_demir = sum([d.toplam_agirlik for d in demirs])
    
    cap_dagilimi = {
        "Q8": sum([d.q8 for d in demirs]),
        "Q10": sum([d.q10 for d in demirs]),
        "Q12": sum([d.q12 for d in demirs]),
        "Q14": sum([d.q14 for d in demirs]),
        "Q16": sum([d.q16 for d in demirs]),
        "Q18": sum([d.q18 for d in demirs]),
        "Q20": sum([d.q20 for d in demirs]),
        "Q22": sum([d.q22 for d in demirs]),
        "Q25": sum([d.q25 for d in demirs]),
        "Q28": sum([d.q28 for d in demirs]),
        "Q32": sum([d.q32 for d in demirs]),
    }
    
    tedarikci_dagilimi = {}
    for d in demirs:
        if d.tedarikci:
            tedarikci_dagilimi[d.tedarikci] = tedarikci_dagilimi.get(d.tedarikci, 0) + d.toplam_agirlik
    
    demir_analytics = {
        "toplam_agirlik": toplam_demir,
        "cap_dagilimi": cap_dagilimi,
        "tedarikci_dagilimi": tedarikci_dagilimi
    }
    
    # Hasir Analytics
    hasirs = db.query(Hasir).all()
    toplam_hasir = sum([h.agirlik for h in hasirs])
    
    hasir_firma_dagilimi = {}
    tip_dagilimi = {}
    
    for h in hasirs:
        hasir_firma_dagilimi[h.firma] = hasir_firma_dagilimi.get(h.firma, 0) + h.agirlik
        if h.hasir_tipi:
            tip_dagilimi[h.hasir_tipi] = tip_dagilimi.get(h.hasir_tipi, 0) + h.agirlik
    
    hasir_analytics = {
        "toplam_agirlik": toplam_hasir,
        "firma_dagilimi": hasir_firma_dagilimi,
        "tip_dagilimi": tip_dagilimi
    }
    
    return {
        "toplam_beton": toplam_beton,
        "toplam_demir": toplam_demir,
        "toplam_hasir": toplam_hasir,
        "beton_analytics": beton_analytics,
        "demir_analytics": demir_analytics,
        "hasir_analytics": hasir_analytics
    }

# ========== EXCEL IMPORT ENDPOINTS ==========

@app.post("/api/import/beton")
async def import_beton_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        df = pd.read_excel(contents, sheet_name='Sayfa1')
        
        # Column mapping
        column_mapping = {
            'TARH': 'TARİH', 'TARİH': 'TARİH',
            'FRMA': 'FİRMA', 'FİRMA': 'FİRMA',
            'RSALYE NO': 'İRSALİYE NO', 'İRSALİYE NO': 'İRSALİYE NO',
            'BETON SINIFI': 'BETON SINIFI',
            'TESLM EKL': 'TESLİM ŞEKLİ', 'TESLİM ŞEKLİ': 'TESLİM ŞEKLİ',
            'MKTAR': 'MİKTAR (m3)', 'MİKTAR': 'MİKTAR (m3)',
            'BLOK': 'BLOK',
            'AIKLAMA': 'AÇIKLAMA', 'AÇIKLAMA': 'AÇIKLAMA'
        }
        
        df = df.rename(columns=column_mapping)
        df = df.dropna(subset=['MİKTAR (m3)'])
        
        count = 0
        for _, row in df.iterrows():
            beton = Beton(
                tarih=pd.to_datetime(row.get('TARİH')),
                firma=row.get('FİRMA'),
                irsaliye_no=str(row.get('İRSALİYE NO', '')),
                beton_sinifi=row.get('BETON SINIFI'),
                teslim_sekli=row.get('TESLİM ŞEKLİ'),
                miktar=float(row.get('MİKTAR (m3)')),
                blok=row.get('BLOK'),
                aciklama=row.get('AÇIKLAMA')
            )
            
            # İrsaliye numarasına göre firma belirleme
            try:
                irsa_num = float(beton.irsaliye_no)
                if irsa_num > 14000:
                    beton.firma = "ALBAYRAK BETON"
                else:
                    beton.firma = "ÖZYURT BETON"
            except:
                pass
            
            db.add(beton)
            count += 1
        
        db.commit()
        return {"message": f"{count} beton kaydı başarıyla eklendi"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Excel import hatası: {str(e)}")

@app.post("/api/import/demir")
async def import_demir_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        df_demir = pd.read_excel(contents, sheet_name=0, header=1)
        
        df_demir.columns = df_demir.columns.astype(str)
        
        # Yardımcı Fonksiyon
        def get_col_by_keyword(columns, keywords, exclude_keywords=[]):
            found_cols = []
            for col in columns:
                if any(kw in col for kw in keywords):
                    if not any(ex in col for ex in exclude_keywords):
                        found_cols.append(col)
            return found_cols

        # Kolon Bulma
        tar_col = get_col_by_keyword(df_demir.columns, ['TAR', 'TARİH'])[0] if get_col_by_keyword(df_demir.columns, ['TAR', 'TARİH']) else None
        etap_col = get_col_by_keyword(df_demir.columns, ['ETAP'])[0] if get_col_by_keyword(df_demir.columns, ['ETAP']) else None
        irsa_col = get_col_by_keyword(df_demir.columns, ['İRSALİYE', 'RSALYE'])[0] if get_col_by_keyword(df_demir.columns, ['İRSALİYE', 'RSALYE']) else None
        tedarik_col = get_col_by_keyword(df_demir.columns, ['SİPARİŞ', 'SPAR'])[0] if get_col_by_keyword(df_demir.columns, ['SİPARİŞ', 'SPAR']) else None
        uretici_col = get_col_by_keyword(df_demir.columns, ['GELDİĞİ', 'GELD'])[0] if get_col_by_keyword(df_demir.columns, ['GELDİĞİ', 'GELD']) else None

        # Çap Kolonları
        q8_cols = get_col_by_keyword(df_demir.columns, ["8'", "8 "], exclude_keywords=["18", "28"])
        q10_cols = get_col_by_keyword(df_demir.columns, ["10'", "10 "])
        q12_cols = get_col_by_keyword(df_demir.columns, ["12'", "12 "])
        q14_cols = get_col_by_keyword(df_demir.columns, ["14'", "14 "])
        q16_cols = get_col_by_keyword(df_demir.columns, ["16'", "16 "])
        q18_cols = get_col_by_keyword(df_demir.columns, ["18'", "18 ", "18L"])
        q20_cols = get_col_by_keyword(df_demir.columns, ["20'", "20 "])
        q22_cols = get_col_by_keyword(df_demir.columns, ["22'", "22 "])
        q25_cols = get_col_by_keyword(df_demir.columns, ["25'", "25 ", "24'", "24 "])
        q28_cols = get_col_by_keyword(df_demir.columns, ["28'", "28 "])
        q32_cols = get_col_by_keyword(df_demir.columns, ["32'", "32 "])
        
        cap_cols_map = {
            8: q8_cols, 10: q10_cols, 12: q12_cols, 14: q14_cols,
            16: q16_cols, 18: q18_cols, 20: q20_cols, 22: q22_cols,
            25: q25_cols, 28: q28_cols, 32: q32_cols
        }

        count = 0
        for _, row in df_demir.iterrows():
            if tar_col and pd.isna(row.get(tar_col)):
                continue
                
            # Çap Ağırlıkları
            cap_values = {}
            for cap, cols in cap_cols_map.items():
                val = 0
                for c in cols:
                    v = pd.to_numeric(row.get(c), errors='coerce')
                    if pd.notna(v):
                        val += v
                cap_values[f'q{cap}'] = val
            
            toplam = sum(cap_values.values())
            
            if toplam > 0:
                demir = Demir(
                    tarih=pd.to_datetime(row.get(tar_col)),
                    etap=row.get(etap_col),
                    irsaliye_no=str(row.get(irsa_col, '')),
                    tedarikci=row.get(tedarik_col),
                    uretici=row.get(uretici_col),
                    toplam_agirlik=toplam,
                    **cap_values
                )
                db.add(demir)
                count += 1
        
        db.commit()
        return {"message": f"{count} demir kaydı başarıyla eklendi"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Excel import hatası: {str(e)}")

@app.post("/api/import/hasir")
async def import_hasir_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        df_hasir = pd.read_excel(contents)
        
        df_hasir.columns = df_hasir.columns.astype(str)
        
        def get_col_by_keyword(columns, keywords):
            for col in columns:
                for kw in keywords:
                    if kw in col:
                        return col
            return None

        tar_col = get_col_by_keyword(df_hasir.columns, ['TARİH', 'TARH'])
        firma_col = get_col_by_keyword(df_hasir.columns, ['FİRMA', 'FRMA'])
        irsa_col = get_col_by_keyword(df_hasir.columns, ['İRSALİYE', 'RSALYE'])
        etap_col = get_col_by_keyword(df_hasir.columns, ['ETAP'])
        tip_col = get_col_by_keyword(df_hasir.columns, ['HASIR TİPİ', 'HASIR TP'])
        boy_col = get_col_by_keyword(df_hasir.columns, ['HASIR UZUNLUĞU', 'HASIR UZUNLUU'])
        en_col = get_col_by_keyword(df_hasir.columns, ['HASIRIN ENİ', 'HASIRIN EN'])
        adet_col = get_col_by_keyword(df_hasir.columns, ['ADET'])
        weight_cols = [c for c in df_hasir.columns if 'AĞIRLIK' in c or 'AIRLIK' in c or 'ARLIK' in c]
        ss_col = get_col_by_keyword(df_hasir.columns, ['SS', 'KULLANIM YERİ'])
        
        count = 0
        for _, row in df_hasir.iterrows():
            if tar_col and pd.isna(row.get(tar_col)):
                continue
            
            # Ebat
            boy_val = row.get(boy_col) if boy_col else None
            en_val = row.get(en_col) if en_col else None
            ebatlar = f"{en_val}x{boy_val}" if pd.notna(boy_val) and pd.notna(en_val) else ""
            
            # Ağırlık
            val = 0
            if weight_cols:
                vals = []
                for c in weight_cols:
                    v = pd.to_numeric(row[c], errors='coerce')
                    if pd.notna(v):
                        vals.append(v)
                if vals:
                    val = max(vals)
            
            adet = pd.to_numeric(row.get(adet_col), errors='coerce') if adet_col else 0
            
            if val > 0 or (adet and adet > 0):
                hasir = Hasir(
                    tarih=pd.to_datetime(row.get(tar_col)),
                    firma=row.get(firma_col),
                    irsaliye_no=str(row.get(irsa_col, '')),
                    etap=row.get(etap_col) or "Genel",
                    hasir_tipi=row.get(tip_col),
                    ebatlar=ebatlar,
                    adet=int(adet) if pd.notna(adet) else None,
                    agirlik=val,
                    kullanim_yeri=row.get(ss_col)
                )
                db.add(hasir)
                count += 1
        
        db.commit()
        return {"message": f"{count} hasır kaydı başarıyla eklendi"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Excel import hatası: {str(e)}")

# ========== ADVANCED ANALYTICS ENDPOINTS ==========

@app.get("/api/analytics/beton/by-date")
def get_beton_by_date(db: Session = Depends(get_db)):
    """Tarihe göre beton dökümü"""
    betons = db.query(Beton).all()
    date_data = {}
    for b in betons:
        date_str = b.tarih.strftime('%Y-%m-%d')
        date_data[date_str] = date_data.get(date_str, 0) + b.miktar
    return {"data": date_data}

@app.get("/api/analytics/demir/by-date")
def get_demir_by_date(db: Session = Depends(get_db)):
    """Tarihe göre demir girişi"""
    demirs = db.query(Demir).all()
    date_data = {}
    for d in demirs:
        date_str = d.tarih.strftime('%Y-%m-%d')
        date_data[date_str] = date_data.get(date_str, 0) + d.toplam_agirlik
    return {"data": date_data}

@app.get("/api/analytics/summary")
def get_summary_stats(db: Session = Depends(get_db)):
    """Özet istatistikler"""
    total_beton = db.query(Beton).count()
    total_demir = db.query(Demir).count()
    total_hasir = db.query(Hasir).count()
    
    return {
        "total_records": {
            "beton": total_beton,
            "demir": total_demir,
            "hasir": total_hasir
        },
        "total_quantities": {
            "beton_m3": sum([b.miktar for b in db.query(Beton).all()]),
            "demir_kg": sum([d.toplam_agirlik for d in db.query(Demir).all()]),
            "hasir_kg": sum([h.agirlik for h in db.query(Hasir).all()])
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


