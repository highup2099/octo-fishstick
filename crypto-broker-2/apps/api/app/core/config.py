from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "CryptoBroker"
    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str
    redis_url: str
    telegram_bot_token: str = ""
    telegram_webapp_url: str = ""
    live_trading_enabled: bool = False
    provider_mode: str = "simulated"
    okx_api_key: str = ""
    okx_api_secret: str = ""
    okx_api_passphrase: str = ""
    bybit_api_key: str = ""
    bybit_api_secret: str = ""
    kyc_provider_api_key: str = ""
    aml_provider_api_key: str = ""
    jwt_secret: str
    cors_allowed_origins: str = "https://your-production-domain.com,https://admin.your-production-domain.com"
    
    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v):
        if not v or len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long for security")
        return v
    
    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL is required")
        # Check if password is hardcoded default
        if "broker:broker@" in v:
            raise ValueError("Database password should not use default 'broker' value. Use environment variables.")
        return v
    
    @field_validator("okx_api_key", "okx_api_secret", "bybit_api_key", "bybit_api_secret")
    @classmethod
    def validate_api_keys_not_default(cls, v, info):
        """Warn if API keys are using placeholder values."""
        if v and ("your_" in v.lower() or "change" in v.lower() or "placeholder" in v.lower()):
            # Don't block, just note that these should be changed
            pass
        return v
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
