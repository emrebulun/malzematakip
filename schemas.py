from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Beton Schemas
class BetonBase(BaseModel):
    tarih: datetime
    firma: str
    irsaliye_no: str
    beton_sinifi: str
    teslim_sekli: str
    miktar: float
    blok: Optional[str] = None
    aciklama: Optional[str] = None

class BetonCreate(BetonBase):
    pass

class BetonResponse(BetonBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Demir Schemas
class DemirBase(BaseModel):
    tarih: datetime
    etap: Optional[str] = None
    irsaliye_no: str
    tedarikci: Optional[str] = None
    uretici: Optional[str] = None
    q8: float = 0
    q10: float = 0
    q12: float = 0
    q14: float = 0
    q16: float = 0
    q18: float = 0
    q20: float = 0
    q22: float = 0
    q25: float = 0
    q28: float = 0
    q32: float = 0
    toplam_agirlik: float

class DemirCreate(DemirBase):
    pass

class DemirResponse(DemirBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Hasir Schemas
class HasirBase(BaseModel):
    tarih: datetime
    firma: str
    irsaliye_no: Optional[str] = None
    etap: Optional[str] = None
    hasir_tipi: Optional[str] = None
    ebatlar: Optional[str] = None
    adet: Optional[int] = None
    agirlik: float
    kullanim_yeri: Optional[str] = None

class HasirCreate(HasirBase):
    pass

class HasirResponse(HasirBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Analytics Schemas
class BetonAnalytics(BaseModel):
    toplam_miktar: float
    firma_dagilimi: dict
    sinif_dagilimi: dict
    blok_dagilimi: dict
    
class DemirAnalytics(BaseModel):
    toplam_agirlik: float
    cap_dagilimi: dict
    tedarikci_dagilimi: dict
    
class HasirAnalytics(BaseModel):
    toplam_agirlik: float
    firma_dagilimi: dict
    tip_dagilimi: dict

class DashboardStats(BaseModel):
    toplam_beton: float
    toplam_demir: float
    toplam_hasir: float
    beton_analytics: BetonAnalytics
    demir_analytics: DemirAnalytics
    hasir_analytics: HasirAnalytics



