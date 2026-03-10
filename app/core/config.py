from typing import List, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "VerboFlete IA"

    # Definimos el tipo como una lista
    ALLOWED_ORIGINS: List[str]

    # Usamos mode='before' para convertir el string del .env en una lista
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    DATABASE_URL: str
    OPENAI_API_KEY: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    ADMIN_INIT_EMAIL: str
    ADMIN_INIT_PASSWORD: str
    ADMIN_NAME: str
    ADMIN_LASTNAME: str

    class Config:
        env_file = ".env"

settings = Settings()