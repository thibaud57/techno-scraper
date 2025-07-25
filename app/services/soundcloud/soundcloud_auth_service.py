import logging
import time

import httpx

from app.core.config import settings
from app.core.errors import AuthenticationException, NetworkException

logger = logging.getLogger(__name__)


class SoundcloudAuthService:
    """Service pour gérer l'authentification OAuth 2.1 avec SoundCloud"""
    TOKEN_URL = "https://api.soundcloud.com/oauth2/token"
    TOKEN_EXPIRY_BUFFER = 300

    def __init__(self):
        self._access_token = None
        self._token_expiry = 0

    async def get_access_token(self) -> str:
        # Si le token n'existe pas ou est expiré, en obtenir un nouveau
        if not self._access_token or time.time() >= self._token_expiry:
            await self._refresh_token()
        return self._access_token

    async def _refresh_token(self) -> None:
        if not settings.SOUNDCLOUD_CLIENT_ID or not settings.SOUNDCLOUD_CLIENT_SECRET:
            raise AuthenticationException(
                message="Les identifiants SoundCloud ne sont pas configurés",
                details={"client_id_configured": bool(settings.SOUNDCLOUD_CLIENT_ID),
                         "client_secret_configured": bool(settings.SOUNDCLOUD_CLIENT_SECRET)}
            )

        try:
            # Préparer les données pour la requête
            data = {
                "grant_type": "client_credentials",
                "client_id": settings.SOUNDCLOUD_CLIENT_ID,
                "client_secret": settings.SOUNDCLOUD_CLIENT_SECRET,
            }

            # Effectuer la requête pour obtenir le token
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self.TOKEN_URL,
                    data=data,
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Accept": "application/json"
                    }
                )

                # Vérifier la réponse
                if response.status_code != 200:
                    error_details = {"status_code": response.status_code}
                    try:
                        error_details["response_body"] = response.json()
                    except Exception:
                        error_details["response_text"] = response.text

                    raise AuthenticationException(
                        message=f"Échec de l'authentification SoundCloud: {response.status_code}",
                        details=error_details
                    )

                # Extraire les données du token
                token_data = response.json()
                self._access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)  # Par défaut 1h

                # Calculer l'expiration avec une marge de sécurité
                self._token_expiry = time.time() + expires_in - self.TOKEN_EXPIRY_BUFFER

                logger.info(
                    "Token d'accès SoundCloud obtenu avec succès (expire dans %s secondes)",
                    expires_in
                )

        except httpx.RequestError as e:
            raise NetworkException(
                message=f"Erreur de réseau lors de l'authentification SoundCloud: {str(e)}",
                details={"error": str(e), "error_type": "network"}
            )
        except Exception as e:
            raise AuthenticationException(
                message=f"Erreur inattendue lors de l'authentification SoundCloud: {str(e)}",
                details={"error": str(e)}
            )

    async def build_auth_url(self, url: str) -> str:
        token = await self.get_access_token()
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}access_token={token}"

    async def get_auth_headers(self) -> dict:
        token = await self.get_access_token()
        return {
            "Authorization": f"OAuth {token}"
        }


# Instance singleton du service d'authentification
soundcloud_auth = SoundcloudAuthService()
