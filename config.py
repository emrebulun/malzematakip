import os
from typing import Optional

class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./santiye_997.db")
    
    # API
    API_TITLE: str = "Şantiye Malzeme Yönetim API"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # CORS
    CORS_ORIGINS: list = ["*"]  # Production'da spesifik domain'ler kullanın
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 100
    MAX_PAGE_SIZE: int = 1000
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = [".xlsx", ".xls"]

settings = Settings()



