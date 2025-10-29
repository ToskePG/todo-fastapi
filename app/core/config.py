from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    EMAIL_TOKEN_EXPIRE_MINUTES: int

    SMTP_SERVER: str
    SMTP_PORT: int
    SENDER_EMAIL: str
    SENDER_PASSWORD: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
