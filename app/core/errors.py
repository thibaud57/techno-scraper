from typing import Any, Dict, Optional

from fastapi import status


class ScraperException(Exception):
    """
    Exception de base pour les erreurs de scraping
    """

    def __init__(
            self,
            message: str,
            status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
            details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class TemporaryScraperException(ScraperException):
    """
    Exception pour les erreurs temporaires qui peuvent être réessayées
    (ex: problèmes de réseau, limites de taux, etc.)
    """

    def __init__(
            self,
            message: str,
            retry_after: Optional[int] = None,
            details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


class PermanentScraperException(ScraperException):
    """
    Exception pour les erreurs permanentes qui ne peuvent pas être réessayées
    (ex: ressource non trouvée, erreur d'authentification, etc.)
    """

    def __init__(
            self,
            message: str,
            status_code: int = status.HTTP_400_BAD_REQUEST,
            details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status_code,
            details=details
        )


class ResourceNotFoundException(PermanentScraperException):
    """
    Exception pour les ressources non trouvées
    """

    def __init__(
            self,
            resource_type: str,
            resource_id: str,
            details: Optional[Dict[str, Any]] = None
    ):
        message = f"{resource_type} avec l'identifiant '{resource_id}' non trouvé"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class RateLimitException(TemporaryScraperException):
    """
    Exception pour les limites de taux
    """

    def __init__(
            self,
            message: str = "Limite de taux atteinte",
            retry_after: Optional[int] = None,
            details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            retry_after=retry_after,
            details=details
        )


class NetworkException(TemporaryScraperException):
    """
    Exception pour les problèmes de réseau
    """

    def __init__(
            self,
            message: str = "Problème de réseau",
            retry_after: Optional[int] = None,
            details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            retry_after=retry_after,
            details=details
        )


class ParsingException(PermanentScraperException):
    """
    Exception pour les erreurs de parsing
    """

    def __init__(
            self,
            message: str = "Erreur lors du parsing des données",
            details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )
