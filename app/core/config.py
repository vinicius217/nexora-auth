from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Nexora"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = Field(
        default="sqlite:///./login.db",
        validation_alias=AliasChoices(
            "NEON_DATABASE_URL",
            "NEON_URL",
            "DATABASE_URL",
        ),
    )
    SECRET_KEY: str = "troque-essa-chave-no-.env-antes-de-ir-pra-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SECURE_COOKIES: bool = False
    DEMO_MODE: bool = False
    DEMO_USER_EMAIL: str = "demo@nexora.dev"
    DEMO_USER_NAME: str = "Nexora Demo"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.ENVIRONMENT.lower() == "production":
            if self.SECRET_KEY == "troque-essa-chave-no-.env-antes-de-ir-pra-producao":
                raise ValueError("Defina uma SECRET_KEY exclusiva antes de iniciar em produção.")
            if not self.SECURE_COOKIES:
                raise ValueError("SECURE_COOKIES deve ser true em produção.")
        return self


settings = Settings()
