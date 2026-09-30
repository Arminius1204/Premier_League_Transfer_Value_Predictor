from backend.app.config import get_settings
from backend.app.services.model_service import ModelService

def get_model_service() -> ModelService:
    settings = get_settings()
    return ModelService(data_path=settings.data_path, models_dir=settings.models_dir)
