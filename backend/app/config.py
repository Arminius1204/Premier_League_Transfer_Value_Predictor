from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from functools import lru_cache

class Settings(BaseSettings):
    # Base path logic handles running from repo root
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    
    data_path: Path = base_dir / "data" / "processed"
    models_dir: Path = base_dir / "models" / "v3"
    
    frontend_origin: str = "http://localhost:3000"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    
    api_football_key: str = ""
    enrichment_path: Path = base_dir / "data" / "player_enrichment"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache()
def get_settings():
    return Settings()
