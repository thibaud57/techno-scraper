from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.core.errors import (ParsingException, ResourceNotFoundException,
                             ScraperException)
from app.core.security import get_api_key
from app.models import (ErrorResponse, SoundcloudProfile, SoundcloudSearchResult,
                       LimitEnum, SocialLink)
from app.scrapers import (
    SoundcloudProfileScraper,
    SoundcloudSearchProfileScraper,
    SoundcloudWebprofilesScraper
)

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
    "/search-profile/{name}",
    response_model=SoundcloudSearchResult,
    summary="Rechercher des profils Soundcloud",
    description="Recherche des profils Soundcloud à partir du nom avec options de pagination",
)
async def search_profiles(
    name: str,
    page: int = 1,
    limit: LimitEnum = LimitEnum.TEN
):
    try:
        scraper = SoundcloudSearchProfileScraper()
        search_results = await scraper.scrape(name, page, limit)
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
    "/profile/{user_id}",
    response_model=SoundcloudProfile,
    summary="Récupérer un profil Soundcloud par ID",
    description="Récupère les informations d'un profil Soundcloud à partir de son ID numérique",
)
async def get_profile(user_id: int):
    try:
        scraper = SoundcloudProfileScraper()
        profile = await scraper.scrape(user_id)
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
    "/profile/{user_id}/webprofiles",
    response_model=List[SocialLink],
    summary="Récupérer les réseaux sociaux d'un profil Soundcloud",
    description="Récupère les liens vers les réseaux sociaux d'un profil Soundcloud à partir de son ID numérique",
)
async def get_profile_webprofiles(user_id: int):
    try:
        scraper = SoundcloudWebprofilesScraper()
        social_links = await scraper.scrape(user_id)
        return social_links
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

