# Tests

Tests unitaires et d'intégration pour techno-scraper.

## Structure

```
tests/
├── integration/    # Tests API complets (TestClient)
├── scrapers/       # Tests unitaires des scrapers  
├── services/       # Tests unitaires des services
└── mocks/          # Mocks réutilisables
```

## Types de tests

- **Unitaires** : Composants isolés avec mocks des dépendances
- **Intégration** : API end-to-end avec mocks des scrapers

## Exécution

```bash
pytest                           # Tous les tests
pytest --cov=app                # Avec couverture
pytest tests/scrapers/          # Tests unitaires seulement
pytest tests/integration/       # Tests d'intégration seulement

# Scripts cross-platform
scripts/run_tests.bat           # Windows
./scripts/run_tests.sh          # Linux/macOS
```

## Patterns de test

Architecture en couches avec mocks appropriés selon le niveau :

- **SoundCloud scrapers** : Mock des services (`@patch('app.services.soundcloud...')`)
- **Beatport/Bandcamp scrapers** : Mock de `BaseScraper.fetch`
- **Services** : Mock des requêtes HTTP (`@patch('httpx.AsyncClient.request')`)
- **Intégration** : Mock des scrapers complets

### Exemple
```python
@pytest.mark.asyncio
@patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
async def test_scraper(self, mock_fetch, scraper):
    mock_fetch.return_value = mock_response_factory(html=MOCK_DATA)
    result = await scraper.scrape(...)
    assert result...
```

## Mocks et conventions

- **Mocks** : `tests/mocks/` (unitaires), `tests/integration/mocks/` (intégration)
- **Async** : Toujours `AsyncMock` pour les fonctions asynchrones
- **Nommage** : `test_*` pour fichiers/méthodes, `Test*` pour classes
- **Isolation** : Tests indépendants avec fixtures ciblées 