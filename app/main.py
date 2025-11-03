import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errors import ScraperException
from app.models import ErrorResponse
from app.routers import soundcloud_router, beatport_router, bandcamp_router

# TODO: [MCP Migration - Phase 4] Ce fichier sera supprimé après migration complète vers MCP
# Actuellement maintenu pour compatibilité REST API pendant la phase de transition

# Configuration du logger
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="API pour scraper des données de sites liés à la musique techno",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Gestionnaire d'exceptions global
@app.exception_handler(ScraperException)
async def scraper_exception_handler(request: Request, exc: ScraperException):
    """
    Gestionnaire d'exceptions pour les erreurs de scraping
    """
    logger.error(f"Erreur de scraping: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details
        ).dict(),
    )


# Inclusion des routers
app.include_router(soundcloud_router.router, prefix=settings.API_PREFIX)
app.include_router(beatport_router.router, prefix=settings.API_PREFIX)
app.include_router(bandcamp_router.router, prefix=settings.API_PREFIX)


# Route racine
@app.get("/", tags=["status"])
async def root():
    """
    Route racine pour vérifier que l'API est en ligne
    """
    return {"message": f"Bienvenue sur l'API {settings.APP_NAME}", "status": "online"}


# Route de statut
@app.get("/status", tags=["status"])
async def status():
    """
    Route de statut pour vérifier que l'API est en ligne
    """
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "version": "0.1.0",
    }


# Point d'entrée pour exécuter l'application directement
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
