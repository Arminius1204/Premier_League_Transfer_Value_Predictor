from backend.app.config import get_settings
from backend.app.services.model_service import ModelService
from backend.app.services.enrichment_service import EnrichmentService
from pathlib import Path
from functools import lru_cache

@lru_cache()
def get_enrichment_service() -> EnrichmentService:
    settings = get_settings()
    metadata_path = settings.enrichment_path / "player_metadata.csv"
    return EnrichmentService(metadata_path=metadata_path)

def get_model_service() -> ModelService:
    settings = get_settings()
    return ModelService(data_path=settings.data_path, models_dir=settings.models_dir, enrichment_service=get_enrichment_service())
