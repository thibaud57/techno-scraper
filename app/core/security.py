from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from app.core.config import settings

# Définition du header pour la clé API
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Utilisez Depends(get_api_key) directement dans les routes ou les routers
async def get_api_key(api_key_header: str = Security(API_KEY_HEADER)):
    if not api_key_header:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Clé API manquante"
        )

    if api_key_header != settings.API_KEY:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Clé API invalide"
        )

    return api_key_header

