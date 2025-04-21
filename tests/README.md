# Tests - TechnoScraper

Ce répertoire contient l'ensemble des tests unitaires et d'intégration du projet TechnoScraper.

## Structure des tests

Les tests sont organisés de façon similaire à la structure du code de l'application :

```
tests/
├── conftest.py          # Configuration globale et fixtures partagées
├── mocks/               # Mocks réutilisables pour les tests
├── scrapers/            # Tests pour les scrapers
│   ├── soundcloud/      # Tests spécifiques pour SoundCloud
│   ├── beatport/        # Tests spécifiques pour Beatport 
│   └── ...              # Tests pour d'autres scrapers
└── services/            # Tests pour les services génériques
```

## Exécution des tests

Pour exécuter les tests, utilisez le script fourni dans le répertoire `scripts` :

```bash
# Sur Windows
.\scripts\run_tests.bat

# Sur Linux/MacOS
./scripts/run_tests.sh
```

## Mocks et fixtures

Le projet utilise des mocks réutilisables pour faciliter les tests :

- Les mocks HTTP : pour simuler les réponses des API externes
- Les mocks des modèles : pour générer des objets de données standardisés
- Les fixtures spécifiques aux services : pour configurer les environnements de test

Ces mocks sont définis dans le répertoire `tests/mocks/` et sont réutilisés à travers les différents tests.

## Tests asynchrones

La plupart des tests utilisent `pytest-asyncio` pour tester les fonctions asynchrones.
Important : 
- Utilisez toujours `AsyncMock` pour mocker les fonctions asynchrones
- La configuration asyncio est définie dans le fichier `pytest.ini` à la racine du projet

Exemple :
```python
@pytest.mark.asyncio
@patch('app.scrapers.some_module.SomeClass.some_method', new_callable=AsyncMock)
async def test_async_function(self, mock_method):
    mock_method.return_value = "some_result"
    # Test code here
```

## Conventions de nommage

- Les noms des fichiers de test commencent par `test_`
- Les classes de test commencent par `Test`
- Les méthodes de test commencent par `test_`

## Bonnes pratiques

1. **Isolation** : Chaque test doit être indépendant des autres tests
2. **Lisibilité** : Le code de test doit être simple et clair
3. **Couverture** : Visez une couverture de code élevée (>90% pour le code métier)
4. **Mocks** : Mocker les dépendances externes (API, bases de données, etc.)
5. **Assertions significatives** : Vérifiez les états, valeurs et comportements importants

## Coverage

Le rapport de couverture de code est généré automatiquement lors de l'exécution des tests. 
Les résultats sont affichés dans la console et peuvent être consultés en détail. 