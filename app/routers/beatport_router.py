from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.core.errors import (ParsingException, ResourceNotFoundException,
                             ScraperException)
from app.core.security import get_api_key
from app.models import (BeatportSearchResult, ErrorResponse,
                        LimitEnum, Release)
from app.models.beatport_models import BeatportEntityType, BeatportReleaseEntityType
from app.scrapers import BeatportReleasesScraper, BeatportSearchScraper

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
    "/{entity_type}/{entity_slug}/releases",
    response_model=List[Release],
    summary="Récupérer les releases d'une entité Beatport",
    description="Récupère les releases d'un artiste ou label Beatport à partir de son slug, ID et type avec options de pagination et filtrage par date",
)
async def get_entity_releases(
        entity_type: BeatportReleaseEntityType,
        entity_slug: str,
        entity_id: str,
        page: int = 1,
        limit: LimitEnum = LimitEnum.TWENTY_FIVE,
        start_date: Optional[date] = Query(None, description="Date de début au format YYYY-MM-DD"),
        end_date: Optional[date] = Query(None, description="Date de fin au format YYYY-MM-DD")
):
    try:
        scraper = BeatportReleasesScraper()
        releases = await scraper.scrape(
            entity_type=BeatportEntityType(entity_type),
            entity_slug=entity_slug,
            entity_id=entity_id,
            page=page,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
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
