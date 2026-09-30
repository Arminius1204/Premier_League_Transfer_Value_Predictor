from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import health, players, models, simulation, similarity, transfers, market
from backend.app.config import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="Premier League Transfer Intelligence API",
    description="API for player valuation, similarity, and what-if simulation.",
    version="1.0.0"
)

# CORS setup
origins = [
    settings.frontend_origin,
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
if settings.frontend_origin not in origins:
    origins.append(settings.frontend_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    # Do not expose raw internal tracebacks
    return Response(content='{"detail": "Internal processing error"}', media_type="application/json", status_code=500)

app.include_router(health.router, tags=["Health"])
app.include_router(players.router, prefix="/players", tags=["Players"])
app.include_router(models.router, prefix="/models", tags=["Models"])
app.include_router(simulation.router, tags=["Simulation"])
app.include_router(similarity.router, prefix="/similarity", tags=["Similarity"])
app.include_router(transfers.router, prefix="/transfers", tags=["Transfers"])
app.include_router(market.router, prefix="/market-analysis", tags=["Market Analysis"])

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing services on startup...")
    # This will trigger validation during startup
    from backend.app.dependencies import get_model_service
    try:
        service = get_model_service()
        if not service.is_healthy():
            raise RuntimeError("Model service failed to initialize correctly.")
    except Exception as e:
        logger.error(f"Failed to start up due to missing artifacts or initialization error: {e}")
        import sys
        sys.exit(1)
