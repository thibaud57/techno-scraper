from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.errors import (ParsingException, ResourceNotFoundException,
                             ScraperException)
from app.core.security import get_api_key
from app.models import (ErrorResponse, SoundcloudProfile,
                                SoundcloudSearchResult)
from app.scrapers import SoundcloudScraper

# Création du router
router = APIRouter(
    prefix="/soundcloud",
    tags=["soundcloud"],
    dependencies=[Depends(get_api_key)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)


@router.get(
    "/profile/{username}",
    response_model=SoundcloudProfile,
    summary="Récupérer un profil Soundcloud",
    description="Récupère les informations d'un profil Soundcloud à partir de son nom d'utilisateur",
)
async def get_profile(username: str):
    try:
        scraper = SoundcloudScraper()
        profile = await scraper.scrape(username)
        return profile
    
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    
    except ParsingException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message,
        )
    
    except ScraperException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur inattendue: {str(e)}",
        )


@router.get(
    "/search",
    response_model=SoundcloudSearchResult,
    summary="Rechercher sur Soundcloud",
    description="Recherche des profils et des tracks sur Soundcloud",
)
async def search(
    query: str = Query(..., description="Terme de recherche"),
    type: Optional[str] = Query(
        None, 
        description="Type de recherche (all, users, tracks)",
        regex="^(all|users|tracks)$"
    ),
    limit: int = Query(10, ge=1, le=100, description="Nombre de résultats à retourner"),
    offset: int = Query(0, ge=0, description="Offset pour la pagination"),
):
    return SoundcloudSearchResult(
        profiles=[],
        tracks=[],
        total_results=0,
        page=offset // limit + 1,
        has_more=False
    )