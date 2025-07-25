import logging
from typing import Dict, Any, Optional, List

import httpx

from app.core.errors import (
    NetworkException,
    PermanentScraperException,
    TemporaryScraperException,
    RateLimitException,
    AuthenticationException
)
from app.services.soundcloud.soundcloud_auth_service import soundcloud_auth
from app.services import with_retry

logger = logging.getLogger(__name__)

class SoundcloudApiService:
    """Service pour interagir avec l'API SoundCloud"""
    API_URL = "https://api.soundcloud.com"
    
    @staticmethod
    @with_retry()
    async def fetch(
            url: str,
            method: str = "GET",
            headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, Any]] = None,
            data: Optional[Dict[str, Any]] = None,
            json: Optional[Dict[str, Any]] = None,
            use_auth_header: bool = True,
    ) -> httpx.Response:
        if use_auth_header:
            token = await soundcloud_auth.get_access_token()
            auth_headers = {"Authorization": f"OAuth {token}"}
            
            # Préparer les headers
            request_headers = {"Accept": "application/json"}
            request_headers.update(auth_headers)
            if headers:
                request_headers.update(headers)
                
            # Utiliser l'URL originale sans modification
            auth_url = url
        else:
            # Méthode alternative: obtenir l'URL authentifiée avec le token en paramètre
            auth_url = await soundcloud_auth.build_auth_url(url)
            # Préparer les headers
            request_headers = {"Accept": "application/json"}
            if headers:
                request_headers.update(headers)
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.request(
                    method=method,
                    url=auth_url,
                    headers=request_headers,
                    params=params,
                    data=data,
                    json=json,
                )
                
                if response.status_code == 429:
                    # Limite de taux atteinte
                    retry_after = response.headers.get("Retry-After")
                    retry_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
                    
                    raise RateLimitException(
                        message=f"Limite de taux atteinte pour {url}",
                        retry_after=retry_seconds,
                        details={"url": url, "status_code": response.status_code}
                    )
                
                elif response.status_code >= 500:
                    # Erreur serveur (temporaire)
                    raise TemporaryScraperException(
                        message=f"Erreur serveur pour {url}: {response.status_code}",
                        details={"url": url, "status_code": response.status_code}
                    )
                
                elif response.status_code == 403:
                    # Erreur d'autorisation (Forbidden)
                    error_details = {"url": url, "status_code": response.status_code}
                    try:
                        error_details["response_body"] = response.json()
                    except Exception:
                        error_details["response_text"] = response.text
                    
                    raise AuthenticationException(
                        message=f"Accès interdit à {url}: vérifiez les autorisations de l'API SoundCloud",
                        details=error_details
                    )
                
                elif response.status_code >= 400 and response.status_code != 404:
                    # Erreur client (permanente)
                    error_details = {"url": url, "status_code": response.status_code}
                    try:
                        error_details["response_body"] = response.json()
                    except Exception:
                        error_details["response_text"] = response.text
                    
                    raise PermanentScraperException(
                        message=f"Erreur client pour {url}: {response.status_code}",
                        status_code=response.status_code,
                        details=error_details
                    )
                
                return response
        
        except httpx.TimeoutException:
            raise NetworkException(
                message=f"Timeout lors de la requête vers {url}",
                details={"url": url, "error_type": "timeout"}
            )
        
        except httpx.RequestError as e:
            raise NetworkException(
                message=f"Erreur de requête vers {url}: {str(e)}",
                details={"url": url, "error_type": "request_error", "error": str(e)}
            )
    
    @classmethod
    async def _fetch_with_auth_fallback(
        cls,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET"
    ) -> httpx.Response:
        """
        Effectue une requête avec fallback automatique en cas d'erreur 403.
        Essaie d'abord avec le header Authorization, puis avec le paramètre d'URL.
        """
        try:
            return await cls.fetch(url, method=method, params=params, use_auth_header=True)
        except AuthenticationException as e:
            logger.warning(
                "Échec de l'authentification avec le header Authorization. "
                "Tentative avec le paramètre d'URL..."
            )
            # En cas d'échec d'authentification, essayer avec le paramètre d'URL
            return await cls.fetch(url, method=method, params=params, use_auth_header=False)
    
    @classmethod
    async def search_users(cls, query: str, limit: int, offset: int = 0) -> Dict[str, Any]:
        """Recherche des utilisateurs SoundCloud"""
        url = f"{cls.API_URL}/users"
        params = {
            "q": query,
            "limit": limit,
            "offset": offset,
            "linked_partitioning": "true"  # Pour la pagination
        }
        response = await cls._fetch_with_auth_fallback(url, params=params)
        return response.json()
    
    @classmethod
    async def get_user(cls, user_id: int) -> Dict[str, Any]:
        """Récupère les informations d'un utilisateur SoundCloud"""
        url = f"{cls.API_URL}/users/{user_id}"
        response = await cls._fetch_with_auth_fallback(url)
        return response.json()
    
    @classmethod
    async def get_user_webprofiles(cls, user_id: int) -> List[Dict[str, Any]]:
        """Récupère les profils web d'un utilisateur SoundCloud"""
        url = f"{cls.API_URL}/users/{user_id}/web-profiles"
        response = await cls._fetch_with_auth_fallback(url)
        return response.json()

# Instance singleton du service API
soundcloud_api = SoundcloudApiService()