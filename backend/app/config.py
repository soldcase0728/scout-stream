from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://scoutstream:scoutstream_dev@localhost:5432/scoutstream"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    upload_dir: str = "./uploads"
    processed_dir: str = "./processed"
    freemocap_version: str = "1.7.4"

    model_config = {"env_prefix": "SCOUT_"}


settings = Settings()
