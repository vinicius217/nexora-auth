from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    APP_NAME: str = "Nexora"
    DATABASE_URL: str = "sqlite:///./login.db"
    SECRET_KEY: str = "troque-essa-chave-no-.env-antes-de-ir-pra-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SECURE_COOKIES: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()
