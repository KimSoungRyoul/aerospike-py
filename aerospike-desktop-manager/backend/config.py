"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str = "Aerospike Desktop Manager"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    default_aerospike_host: str = "127.0.0.1"
    default_aerospike_port: int = 3000
    metrics_poll_interval: float = 2.0  # seconds for WebSocket polling

    model_config = {"env_prefix": "ADM_"}


settings = Settings()
