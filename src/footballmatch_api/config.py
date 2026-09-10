from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "FootballMatch AI Platform"
    app_version: str = "0.1.0"
    environment: str = "local"

    model_config = SettingsConfigDict(env_prefix="FOOTBALLMATCH_", env_file=".env")


settings = Settings()
