from pydantic_settings import BaseSettings
from typing import List
import json

class Settings(BaseSettings):
    # API Keys
    GEMINI_API_KEY: str
    FIREBASE_CREDENTIALS_PATH: str
    
    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # CORS
    CORS_ORIGINS: str = '["http://localhost:5173"]'
    
    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)
    
    # App Config
    APP_NAME: str = "AI Document Generator"
    APP_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
