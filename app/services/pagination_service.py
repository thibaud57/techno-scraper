import logging
from typing import List, TypeVar

from app.models import LimitEnum

logger = logging.getLogger(__name__)

T = TypeVar('T')

class PaginationService:
    """Service pour gérer la pagination des résultats"""
    
    @staticmethod
    def paginate_results(results: List[T], page: int, limit: LimitEnum) -> List[T]:
        start_idx = (page - 1) * limit.value
        end_idx = start_idx + limit.value
        
        # Vérifier si l'index de début est valide
        if start_idx < len(results):
            return results[start_idx:end_idx]
        else:
            # Si la page demandée dépasse le nombre de résultats disponibles, retourner une liste vide
            logger.warning(f"Page {page} demandée mais seulement {len(results)} résultats disponibles")
            return []