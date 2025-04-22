from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.core.errors import (ParsingException, ResourceNotFoundException,
                             ScraperException)
from app.core.security import get_api_key
from app.models import (ErrorResponse, BeatportProfile, BeatportSearchResult,
                       LimitEnum, Release)
from app.models.beatport_models import BeatportEntityType
from app.scrapers import (
    BeatportSearchScraper,
    BeatportReleasesScraper
)

# Création du router
router = APIRouter(
    prefix="/beatport",
    tags=["beatport"],
    dependencies=[Depends(get_api_key)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)


@router.get(
    "/search/{query}",
    response_model=BeatportSearchResult,
    summary="Rechercher sur Beatport",
    description="Recherche des artistes, tracks et releases sur Beatport à partir d'un terme de recherche avec options de pagination et filtrage par type d'entité",
)
async def search(
    query: str,
    page: int = 1,
    limit: LimitEnum = LimitEnum.TEN,
    entity_type: BeatportEntityType = None
):
    try:
        scraper = BeatportSearchScraper()
        search_results = await scraper.scrape(query, page, limit, entity_type)
        return search_results
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
    "/artist/{artist_slug}/releases",
    response_model=List[Release],
    summary="Récupérer les releases d'un artiste Beatport",
    description="Récupère les releases d'un artiste Beatport à partir de son slug avec options de pagination",
)
async def get_artist_releases(
    artist_slug: str,
    page: int = 1,
    limit: LimitEnum = LimitEnum.TEN
):
    try:
        scraper = BeatportReleasesScraper()
        releases = await scraper.scrape(artist_slug, page, limit)
        return releases
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