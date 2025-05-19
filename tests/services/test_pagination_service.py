from app.models import LimitEnum
from app.services.pagination_service import PaginationService


class TestPaginationService:

    def test_pagination_empty_results(self):
        results = []
        paginated = PaginationService.paginate_results(results, page=1, limit=LimitEnum.TEN)
        assert paginated == []

    def test_pagination_first_page(self):
        """Teste la pagination pour la première page"""
        results = list(range(25))
        paginated = PaginationService.paginate_results(results, page=1, limit=LimitEnum.TEN)
        assert paginated == list(range(10))  # Premiers 10 éléments
        assert len(paginated) == 10

    def test_pagination_second_page(self):
        """Teste la pagination pour la deuxième page"""
        results = list(range(25))
        paginated = PaginationService.paginate_results(results, page=2, limit=LimitEnum.TEN)
        assert paginated == list(range(10, 20))  # Éléments 10-19
        assert len(paginated) == 10

    def test_pagination_last_page(self):
        """Teste la pagination pour la dernière page (qui n'est pas complète)"""
        results = list(range(25))
        paginated = PaginationService.paginate_results(results, page=3, limit=LimitEnum.TEN)
        assert paginated == list(range(20, 25))  # Éléments 20-24
        assert len(paginated) == 5

    def test_pagination_out_of_range(self):
        """Teste la pagination pour une page qui n'existe pas"""
        results = list(range(25))
        paginated = PaginationService.paginate_results(results, page=4, limit=LimitEnum.TEN)
        assert paginated == []  # Page vide car hors limites

    def test_pagination_different_limits(self):
        """Teste la pagination avec différentes limites"""
        results = list(range(50))

        # Test avec une limite de 5
        paginated = PaginationService.paginate_results(results, page=1, limit=LimitEnum.FIVE)
        assert paginated == list(range(5))
        assert len(paginated) == 5

        # Test avec une limite de 25
        paginated = PaginationService.paginate_results(results, page=1, limit=LimitEnum.TWENTY_FIVE)
        assert paginated == list(range(25))
        assert len(paginated) == 25

        # Test avec une limite de 50
        paginated = PaginationService.paginate_results(results, page=1, limit=LimitEnum.FIFTY)
        assert paginated == list(range(50))
        assert len(paginated) == 50 