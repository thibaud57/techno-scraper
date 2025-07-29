from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.core.errors import (ParsingException, ResourceNotFoundException,
                             ScraperException)
from app.core.security import get_api_key
from app.models import (ErrorResponse, BandcampSearchResult, BandcampEntityType)
from app.scrapers import BandcampSearchScraper

# Création du router
router = APIRouter(
    prefix="/bandcamp",
    tags=["bandcamp"],
    dependencies=[Depends(get_api_key)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)


@router.get(
    "/search",
    response_model=BandcampSearchResult,
    summary="Rechercher sur Bandcamp",
    description="Recherche d'artistes, labels, albums ou tracks sur Bandcamp avec options de pagination",
)
async def search(
        query: str,
        page: int = 1,
        entity_type: BandcampEntityType = Query(BandcampEntityType.BANDS, description="Type d'entité à rechercher (b=artistes et labels, t=pistes)"),
):
    try:
        scraper = BandcampSearchScraper()
        search_results = await scraper.scrape(query, page, entity_type)
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
