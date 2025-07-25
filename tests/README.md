# Tests - TechnoScraper

Ce répertoire contient l'ensemble des tests unitaires et d'intégration du projet TechnoScraper.

## Structure des tests

Les tests sont organisés de façon similaire à la structure du code de l'application :

```
tests/
├── conftest.py          # Configuration globale et fixtures partagées
├── integration/         # Tests d'intégration
│   ├── mocks/           # Mocks spécifiques aux tests d'intégration
│   ├── test_api_routes.py  # Tests des routes API générales
│   ├── test_beatport_router.py  # Tests des routes Beatport
│   └── test_soundcloud_router.py  # Tests des routes Soundcloud
├── mocks/               # Mocks réutilisables optimisés pour les tests unitaires
├── scrapers/            # Tests unitaires pour les scrapers
│   ├── soundcloud/      # Tests spécifiques pour SoundCloud
│   ├── beatport/        # Tests spécifiques pour Beatport
│   └── ...              # Tests pour d'autres scrapers
└── services/            # Tests unitaires pour les services
    ├── soundcloud/      # Tests des services SoundCloud
    ├── test_retry_service.py  # Tests pour le service de retry
    └── test_pagination_service.py  # Tests pour le service de pagination
```

## Types de tests

### Tests unitaires

Les tests unitaires vérifient le comportement isolé de chaque composant de l'application, comme les scrapers individuels ou les services utilitaires. Ils utilisent des mocks pour remplacer les dépendances externes.

### Tests d'intégration

Les tests d'intégration vérifient que les différentes parties de l'application fonctionnent correctement ensemble, en se concentrant sur les points d'interaction entre les composants. Ils utilisent `TestClient` de FastAPI pour simuler des requêtes HTTP vers l'API et des mocks pour simuler les réponses des services externes.

## Exécution des tests

Pour exécuter tous les tests :

```bash
# Sur Windows
.\scripts\run_tests.bat

# Sur Linux/MacOS
./scripts/run_tests.sh
```

Pour exécuter uniquement les tests unitaires :

```bash
pytest -v tests/scrapers/ tests/services/
```

Pour exécuter uniquement les tests d'intégration :

```bash
pytest -v tests/integration/
```

Pour exécuter les tests avec couverture de code :

```bash
# Tous les tests avec couverture
pytest -v --cov=app tests/

# Tests d'intégration avec couverture
pytest -v --cov=app.routers tests/integration/
```

## Structure et pattern de test

Les tests suivent une structure cohérente à travers les différents modules :

- Utilisation de fixtures pytest pour créer les instances de scrapers, réduisant la duplication de code
- Utilisation de décorateurs `@patch` pour mocker les dépendances externes
- Standardisation des entrées/sorties des tests pour faciliter les comparaisons
- Tests pour les cas nominaux et les cas d'erreur

### Pattern décoratif uniformisé

Les tests suivent des patterns adaptés selon le niveau de test :

**Tests des scrapers (mockent les services) :**
```python
@pytest.mark.asyncio
@patch('app.services.soundcloud.soundcloud_api_service.SoundcloudApiService.get_user', new_callable=AsyncMock)
async def test_example(self, mock_get_user, scraper, mock_data):
    # Configuration des mocks au niveau service
    mock_get_user.return_value = mock_data
    
    # Appel de la méthode sous test
    result = await scraper.scrape(...)
    
    # Assertions
    assert result...
```

**Tests des services (mockent les requêtes HTTP) :**
```python
@pytest.mark.asyncio
@patch('httpx.AsyncClient.request', new_callable=AsyncMock)
async def test_service(self, mock_request, service):
    # Configuration des mocks HTTP
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_request.return_value = mock_response
    
    # Test du service
    result = await service.method(...)
    
    # Assertions
    assert result...
```

Cette approche en couches facilite la maintenance et assure une séparation claire des responsabilités.

## Mocks et fixtures

Le projet utilise des mocks optimisés et réutilisables pour faciliter les tests :

- **Mocks HTTP** : pour simuler les réponses des API externes
- **Mocks des modèles** : pour générer des objets de données standardisés
- **Fixtures spécifiques aux services** : pour configurer les environnements de test
- **Mocks d'authentification** : pour les identifiants SoundCloud (utilisés de manière ciblée)

### Organisation des mocks

- `tests/mocks/` : Mocks pour les tests unitaires (optimisés, sans redondances)
- `tests/integration/mocks/` : Mocks spécifiques aux tests d'intégration
- Fixtures utilisées de manière ciblée (pas d'`autouse=True` inutile)

Ces mocks sont réutilisés à travers les différents tests et suivent les bonnes pratiques de test.

## Tests asynchrones

La plupart des tests utilisent `pytest-asyncio` pour tester les fonctions asynchrones.
Important : 
- Utilisez toujours `AsyncMock` pour mocker les fonctions asynchrones
- La configuration asyncio est définie dans le fichier `pytest.ini` à la racine du projet

Exemple :
```python
@pytest.mark.asyncio
@patch('app.scrapers.some_module.SomeClass.some_method', new_callable=AsyncMock)
async def test_async_function(self, mock_method, scraper):
    mock_method.return_value = "some_result"
    # Test code here
```

## Conventions de nommage

- Les noms des fichiers de test commencent par `test_`
- Les classes de test commencent par `Test`
- Les méthodes de test commencent par `test_`
- Dans les tests d'intégration, les fixtures et méthodes de test n'utilisent pas de suffixe `_integration` pour rester concis et lisibles

## Bonnes pratiques

1. **Isolation** : Chaque test doit être indépendant des autres tests
2. **Lisibilité** : Le code de test doit être simple et clair
3. **Couverture** : Visez une couverture de code élevée (>90% pour le code métier)
4. **Mocks** : Mocker les dépendances externes (API, bases de données, etc.)
5. **Assertions significatives** : Vérifiez les états, valeurs et comportements importants

## Coverage

Le rapport de couverture de code est généré automatiquement lors de l'exécution des tests. 
Les résultats sont affichés dans la console et peuvent être consultés en détail.

## Tests d'API

Les tests d'intégration des API (`tests/integration/`) vérifient que les routes API fonctionnent correctement de bout en bout :

- Validation des entrées et sorties conformes aux modèles Pydantic
- Gestion correcte des erreurs et des cas limites
- Intégration des middlewares (authentification, logging, etc.)

Pour les tests d'API, nous utilisons `TestClient` de FastAPI qui permet de faire des requêtes HTTP simulées sans serveur réel.

## Services

Les tests des services (`tests/services/`) vérifient les fonctionnalités des composants génériques de l'application :

- **Service de retry** : gestion des tentatives en cas d'échecs temporaires (synchrone et asynchrone)

Pour tester un service spécifique avec couverture de code :

```bash
python -m pytest tests/services/test_nom_service.py -v --cov=app.services.nom_service
``` 