import logging
import time
from functools import wraps
from typing import Any, Callable, List, Type, TypeVar, cast

from tenacity import (RetryError, before_sleep_log, retry,
                      retry_if_exception_type, stop_after_attempt,
                      wait_exponential)

from app.core.config import settings
from app.core.errors import (PermanentScraperException, ScraperException,
                             TemporaryScraperException)

logger = logging.getLogger(__name__)

# Type générique pour la fonction décorée
F = TypeVar("F", bound=Callable[..., Any])


def with_retry(
        max_attempts: int = None,
        retry_exceptions: List[Type[Exception]] = None,
        min_wait: float = 1.0,
        max_wait: float = 10.0,
) -> Callable[[F], F]:
    if max_attempts is None:
        max_attempts = settings.MAX_RETRIES

    if retry_exceptions is None:
        retry_exceptions = [TemporaryScraperException]

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                # Utilisation de tenacity pour gérer les retries
                @retry(
                    stop=stop_after_attempt(max_attempts),
                    wait=wait_exponential(multiplier=settings.RETRY_BACKOFF_FACTOR, min=min_wait, max=max_wait),
                    retry=retry_if_exception_type(tuple(retry_exceptions)),
                    before_sleep=before_sleep_log(logger, logging.INFO),
                    reraise=True,
                )
                def _wrapped_func() -> Any:
                    return func(*args, **kwargs)

                return _wrapped_func()

            except RetryError as e:
                # Si toutes les tentatives ont échoué, on récupère la dernière exception
                last_exception = e.last_attempt.exception()

                if isinstance(last_exception, TemporaryScraperException):
                    # Convertir l'exception temporaire en exception permanente après tous les retries
                    raise PermanentScraperException(
                        message=f"Échec après {max_attempts} tentatives: {str(last_exception)}",
                        status_code=last_exception.status_code,
                        details={
                            "original_error": str(last_exception),
                            "attempts": max_attempts,
                            **last_exception.details
                        }
                    )

                # Si c'est déjà une exception permanente ou une autre exception, on la relève
                raise last_exception

            except Exception as e:
                # Pour les exceptions non gérées
                if not isinstance(e, ScraperException):
                    # Convertir les exceptions standard en ScraperException
                    raise ScraperException(
                        message=f"Erreur inattendue: {str(e)}",
                        details={"original_error": str(e), "error_type": type(e).__name__}
                    )
                raise

        return cast(F, wrapper)

    return decorator


async def async_with_retry(
        func: Callable,
        max_attempts: int = None,
        retry_exceptions: List[Type[Exception]] = None,
        min_wait: float = 1.0,
        max_wait: float = 10.0,
        *args: Any,
        **kwargs: Any
) -> Any:
    if max_attempts is None:
        max_attempts = settings.MAX_RETRIES

    if retry_exceptions is None:
        retry_exceptions = [TemporaryScraperException]

    attempt = 0
    last_exception = None

    while attempt < max_attempts:
        try:
            return await func(*args, **kwargs)

        except tuple(retry_exceptions) as e:
            attempt += 1
            last_exception = e

            if attempt >= max_attempts:
                break

            # Calcul du temps d'attente avec backoff exponentiel
            wait_time = min(max_wait, min_wait * (2 ** (attempt - 1)))

            logger.info(
                f"Tentative {attempt}/{max_attempts} échouée: {str(e)}. "
                f"Nouvelle tentative dans {wait_time:.2f} secondes."
            )

            # Attente avant la prochaine tentative
            time.sleep(wait_time)

        except Exception as e:
            # Pour les exceptions non gérées ou permanentes
            if not isinstance(e, ScraperException):
                # Convertir les exceptions standard en ScraperException
                raise ScraperException(
                    message=f"Erreur inattendue: {str(e)}",
                    details={"original_error": str(e), "error_type": type(e).__name__}
                )
            raise

    # Si toutes les tentatives ont échoué
    if isinstance(last_exception, TemporaryScraperException):
        # Convertir l'exception temporaire en exception permanente après tous les retries
        raise PermanentScraperException(
            message=f"Échec après {max_attempts} tentatives: {str(last_exception)}",
            status_code=last_exception.status_code,
            details={
                "original_error": str(last_exception),
                "attempts": max_attempts,
                **last_exception.details
            }
        )

    # Si c'est déjà une exception permanente ou une autre exception, on la relève
    raise last_exception
