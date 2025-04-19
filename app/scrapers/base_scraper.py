import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import httpx
from fake_useragent import UserAgent

from app.core.config import settings
from app.core.errors import (NetworkException, PermanentScraperException,
                             RateLimitException, TemporaryScraperException)
from app.services.retry_service import with_retry

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    def __init__(self, timeout: int = None, user_agent: str = None):
        self.timeout = timeout or settings.REQUEST_TIMEOUT
        self.user_agent = user_agent or settings.USER_AGENT

        # Utiliser fake-useragent si aucun user-agent n'est spécifié
        if not self.user_agent or self.user_agent == "random":
            try:
                ua = UserAgent()
                self.user_agent = ua.random
            except Exception as e:
                logger.warning(f"Impossible de générer un User-Agent aléatoire: {e}")
                self.user_agent = settings.USER_AGENT

    @with_retry()
    async def fetch(
            self,
            url: str,
            method: str = "GET",
            headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, Any]] = None,
            data: Optional[Dict[str, Any]] = None,
            json: Optional[Dict[str, Any]] = None,
            follow_redirects: bool = True,
    ) -> httpx.Response:
        request_headers = {"User-Agent": self.user_agent}
        if headers:
            request_headers.update(headers)

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=follow_redirects) as client:
                response = await client.request(
                    method=method,
                    url=url,
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

                elif response.status_code >= 400 and response.status_code != 404:
                    # Erreur client (permanente)
                    raise PermanentScraperException(
                        message=f"Erreur client pour {url}: {response.status_code}",
                        status_code=response.status_code,
                        details={"url": url, "status_code": response.status_code}
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

        except httpx.HTTPStatusError as e:
            raise TemporaryScraperException(
                message=f"Erreur HTTP pour {url}: {str(e)}",
                details={"url": url, "error_type": "http_status_error", "error": str(e)}
            )

    @abstractmethod
    async def scrape(self, *args: Any, **kwargs: Any) -> Any:
        """
        Méthode abstraite à implémenter par les classes dérivées
        pour effectuer le scraping
        """
        pass
