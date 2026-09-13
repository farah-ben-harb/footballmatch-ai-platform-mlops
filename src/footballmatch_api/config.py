from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "FootballMatch AI Platform"
    app_version: str = "0.1.0"
    environment: str = "local"
    max_upload_size_bytes: int = 100_000_000
    runtime_directory: str = "runtime"
    mlflow_tracking_uri: str | None = None
    mlflow_experiment_name: str = "football-video-analysis"

    model_config = SettingsConfigDict(env_prefix="FOOTBALLMATCH_", env_file=".env")


settings = Settings()
