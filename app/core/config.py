from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    FRONTEND_URL: str = "http://localhost:3000"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalise_db_url(cls, v: str) -> str:
        # Neon / Render give postgres:// or postgresql:// — asyncpg needs postgresql+asyncpg://
        if v.startswith("postgres://"):
            v = "postgresql+asyncpg://" + v[len("postgres://"):]
        elif v.startswith("postgresql://") and "+asyncpg" not in v:
            v = "postgresql+asyncpg://" + v[len("postgresql://"):]
        # asyncpg doesn't understand sslmode query param
        v = v.replace("sslmode=require", "ssl=require").replace("sslmode=prefer", "ssl=prefer")
        return v

    class Config:
        env_file = ".env"


settings = Settings()
