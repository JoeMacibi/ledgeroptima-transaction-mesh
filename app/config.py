import os
from typing import Literal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "LedgerOptima Telemetry Dashboard"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/telemetry"
    )
    
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    
    transaction_batch_size: int = 1000
    anomaly_check_interval: int = 300
    synthetic_data_rate: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
