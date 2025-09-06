from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # These are the ONLY variables our Python code needs to load
    DATABASE_URL: str
    secret_key: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings()