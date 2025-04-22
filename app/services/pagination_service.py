import logging
from typing import List, TypeVar, Generic, Any

from app.models import LimitEnum

logger = logging.getLogger(__name__)

T = TypeVar('T')

class PaginationService:
    """Service pour gérer la pagination des résultats"""
    
    @staticmethod
    def paginate_results(results: List[T], page: int, limit: LimitEnum) -> List[T]:
        """
        Applique la pagination à une liste de résultats.
        
        Args:
            results: La liste complète des résultats à paginer
            page: Le numéro de page (commence à 1)
            limit: Le nombre de résultats par page
            
        Returns:
            List[T]: Les résultats paginés
        """
        # Calculer l'index de début et de fin pour la pagination
        start_idx = (page - 1) * limit.value
        end_idx = start_idx + limit.value
        
        # Vérifier si l'index de début est valide
        if start_idx < len(results):
            return results[start_idx:end_idx]
        else:
            # Si la page demandée dépasse le nombre de résultats disponibles, retourner une liste vide
            logger.debug(f"Page {page} demandée mais seulement {len(results)} résultats disponibles")
            return []