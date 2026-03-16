"""
Configuration settings for the ETL pipeline.
Uses environment variables for sensitive data.
"""
import os
from dataclasses import dataclass
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ARCHIVE_DATA_DIR = DATA_DIR / "archive"

# Create directories if they don't exist
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, ARCHIVE_DATA_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    database: str = os.getenv("DB_NAME", "sales_dwh")
    user: str = os.getenv("DB_USER", "etl_user")
    password: str = os.getenv("DB_PASSWORD", "")
    
    @property
    def connection_string(self) -> str:
        """Return SQLAlchemy connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class ETLConfig:
    """ETL pipeline configuration."""
    batch_size: int = int(os.getenv("ETL_BATCH_SIZE", "10000"))
    max_retries: int = int(os.getenv("ETL_MAX_RETRIES", "3"))
    retry_delay_seconds: int = int(os.getenv("ETL_RETRY_DELAY", "60"))
    enable_quality_checks: bool = os.getenv("ETL_QUALITY_CHECKS", "true").lower() == "true"


# Singleton instances
db_config = DatabaseConfig()
etl_config = ETLConfig()
