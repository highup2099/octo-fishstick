from pydantic_settings import BaseSettings, SettingsConfigDict

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
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
