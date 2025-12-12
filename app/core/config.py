
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Organization Management Service"
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "org_management_db"
    SECRET_KEY: str = "secret"  # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
