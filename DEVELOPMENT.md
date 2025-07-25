# Journal de développement - techno-scraper

Ce document résume l'état actuel du projet, les fonctionnalités implémentées, et les prochaines étapes prévues.

## État actuel du projet (25/07/2025)

Le projet techno-scraper est une API FastAPI conçue pour scraper des données de différents sites liés à la musique techno (Soundcloud, Beatport, Bandcamp, Facebook, Instagram, Songstats). L'API est destinée à être utilisée par n8n pour automatiser des workflows de récupération de données.

### Structure implémentée

-   Architecture en couches (routers, services, models, scrapers)
-   Configuration Docker pour le développement local et le déploiement
-   Configuration GitHub Actions pour le déploiement automatique sur VPS
-   Scripts utilitaires pour le développement local
-   Suite complète de tests unitaires et d'intégration

### Fonctionnalités implémentées

-   Structure de base de l'application FastAPI
-   Authentification par clé API
-   Gestion des erreurs et des retries
-   Modèles de données pour les résultats et la pagination
-   Support des scrapers modulaires avec BaseScraper
-   Service de retries
-   Scraper pour Soundcloud
    - Recherche de profils
    - Profil (par ID)
    - Réseaux sociaux
-   Scraper pour Beatport
    - Recherche
    - Releases (artiste/label)
-   Infrastructure de tests
    - Tests unitaires pour tous les scrapers
    - Tests d'intégration des endpoints API
    - Mocks pour les réponses externes

### Modifications récentes (25/07/2025)

-   **Refactorisation majeure de l'architecture SoundCloud**
    - Implémentation de l'authentification OAuth 2.1 avec Client Credentials Flow
    - Création de services SoundCloud dédiés (`SoundcloudAuthService`, `SoundcloudApiService`)
    - Séparation claire des responsabilités entre authentification et API
    - Correction de l'URL de base API SoundCloud (`https://api.soundcloud.com`)
    - Utilisation du format d'authentification correct (`OAuth ACCESS_TOKEN`)
    - Suppression du paramètre `redirect_uri` inutile pour le Client Credentials Flow
    - Amélioration de l'organisation du code avec des packages et imports propres

-   **Mise à jour complète de l'architecture de test**
    - Migration des tests des scrapers pour utiliser les nouveaux services SoundCloud
    - Création de tests complets pour les services SoundCloud
    - Optimisation des mocks et fixtures (suppression des redondances)
    - Correction des signatures d'exceptions (`ResourceNotFoundException`)
    - Architecture de test en couches : tests unitaires mockent les services, tests d'intégration mockent les scrapers

-   **Corrections techniques importantes**
    - Correction du mapping des webprofiles SoundCloud (support des clés "service" et "network")
    - Extension du modèle `SocialLink` pour supporter Twitter et YouTube
    - Mise à jour des mocks de test pour utiliser le format correct de l'API SoundCloud
    - Gestion d'erreurs améliorée avec mécanismes de fallback
    - Configuration des variables d'environnement SoundCloud dans GitHub Actions

### Modifications précédentes (19/05/2025)

-   Refactorisation complète et unification de la logique de test
    - Standardisation de l'approche des tests pour tous les scrapers
    - Adoption d'un pattern décoratif uniforme avec `@patch` et `AsyncMock`
    - Ajout de fixtures pour les scrapers, réduisant la duplication de code
    - Implémentation complète des tests pour les scrapers Beatport (search et releases)
    - Alignement de la logique de test entre les scrapers SoundCloud et Beatport
    - Amélioration de la maintenabilité et de la lisibilité des tests
    - Mise en place d'un pattern cohérent facilitant l'ajout de nouveaux scrapers
    - Élimination du code boilerplate grâce aux fixtures et aux décorateurs

### Modifications précédentes (02/05/2025)

-   Amélioration du scraper Beatport releases
    - Support des releases par artiste et par label dans un endpoint unifié
    - Implémentation du filtrage par date avec format YYYY-MM-DD
    - Support de la pagination côté serveur Beatport
    - Extraction améliorée des métadonnées des releases (artwork, track_count)
    - Adaptation flexible aux différentes structures de données JSON
    - Support des URLs au format nouveau (id/name) et ancien (release_id/release_name)
    - Optimisation du mapping des images avec une gestion unifiée des placeholders
    - Extraction de données supplémentaires comme le nombre de tracks

### Modifications précédentes (22/04/2025)

-   Implémentation du scraper Beatport
    - Scraper de recherche avec filtrage par type d'entité (artistes, tracks, releases, labels)
    - Support de la pagination avec numéro de page et limite
    - Extraction des données depuis le script NEXT_DATA de Beatport
    - Mappage des données vers les modèles standardisés
-   Création d'un service de pagination réutilisable
    - Extraction de la logique de pagination dans `PaginationService`
    - Implémentation dans les scrapers Beatport
    - Pagination correcte en fonction du numéro de page et de la limite
-   Amélioration de l'architecture des scrapers
    - Adoption d'une approche plus immuable (programmation fonctionnelle)
    - Utilisation de `match/case` (Python 3.10+) pour un code plus lisible
    - Réduction du boilerplate code et meilleure organisation

### Modifications précédentes (21/04/2025)

-   Implémentation des tests unitaires et d'intégration
    - Tests unitaires pour tous les scrapers (notamment SoundCloud)
    - Tests d'intégration couvrant tous les endpoints de l'API
    - Configuration des mocks pour simuler les réponses des API externes
    - Amélioration de la testabilité du code avec l'injection de dépendances
-   Optimisation des scripts et workflows GitHub
    - Correction et amélioration des workflows GitHub Actions
    - Configuration des workflows deploy.yml, build.yml et test.yml
    - Automatisation des tests pour chaque pull request
    - Configuration du déploiement continu sur le VPS
    - Ajout de la génération automatique de rapports de couverture de code
    - Intégration d'un linter et de vérifications de qualité de code

### Modifications précédentes (19/04/2025)

-   Optimisation majeure des scrapers Soundcloud avec requêtes concurrentes
-   Implémentation de l'extraction des réseaux sociaux via l'API web-profiles
-   Refactorisation du scraper de profil pour récupérer le profil et les réseaux sociaux en parallèle
-   Amélioration du scraper de recherche pour récupérer les réseaux sociaux pour tous les profils trouvés
-   Standardisation de l'approche asynchrone avec asyncio pour de meilleures performances
-   Amélioration des performances avec l'extraction parallèle des réseaux sociaux
-   Réduction du boilerplate code dans les scrapers
-   Meilleure gestion des erreurs pour les appels API concurrents

### Problèmes résolus

-   Correction d'une erreur de dépendance FastAPI (`AssertionError: A parameter-less dependency must have a callable dependency`)
    -   Solution : Utilisation correcte de `Depends(get_api_key)` au lieu de `Depends(api_key_auth)`
-   Restructuration des modules pour éviter les imports circulaires
-   Amélioration de la gestion des réponses d'API externes
-   Résolution des problèmes de lookup par username avec une approche basée sur les IDs
-   Simplification de l'interface de l'API pour une utilisation plus intuitive
-   Optimisation de la récupération des réseaux sociaux avec des requêtes concurrentes
-   Meilleur mappage des types de réseaux sociaux aux plateformes standardisées
-   Correction des scripts de déploiement pour une meilleure stabilité
-   Résolution de problèmes d'intégration continue dans les workflows GitHub

## Intégration API SoundCloud

L'API SoundCloud utilisée par notre scraper a été complètement refactorisée avec une architecture moderne :

### Architecture des Services

-   **SoundcloudAuthService** : Gestion de l'authentification OAuth 2.1
    -   Client Credentials Flow pour l'accès aux ressources publiques
    -   Gestion automatique du renouvellement des tokens
    -   Format d'authentification correct : `OAuth ACCESS_TOKEN`
    -   URL d'authentification : `https://api.soundcloud.com/oauth2/token`

-   **SoundcloudApiService** : Interface unifiée pour les appels API
    -   URL de base corrigée : `https://api.soundcloud.com`
    -   Gestion des erreurs avec retry et fallback
    -   Support des headers d'authentification et des paramètres URL
    -   Méthodes dédiées : `get_user()`, `search_users()`, `get_user_webprofiles()`

### Authentification OAuth 2.1

-   **Client Credentials Flow** implémenté correctement
-   Variables d'environnement requises :
    -   `SOUNDCLOUD_CLIENT_ID` : ID de l'application SoundCloud
    -   `SOUNDCLOUD_CLIENT_SECRET` : Secret de l'application SoundCloud
-   Suppression du paramètre `redirect_uri` inutile pour le Client Credentials Flow
-   Gestion automatique de l'expiration des tokens avec marge de sécurité

### Fonctionnalités implémentées

-   Recherche de profils via l'endpoint `/search/users` avec paramètre `q`
-   Récupération de profils via l'endpoint `/users/{id}`
-   Récupération des réseaux sociaux via l'endpoint `/users/{id}/web-profiles`
-   Support de la pagination avec les paramètres `offset` et `limit`
-   Gestion des erreurs avec les codes HTTP appropriés
-   Exécution concurrente des requêtes pour de meilleures performances
-   Support étendu des plateformes sociales (Facebook, Instagram, sites web, ...)

### Améliorations techniques

-   Correction du mapping des webprofiles (support des clés "service" et "network")
-   Gestion d'erreurs robuste avec exceptions typées
-   Architecture en couches avec séparation des responsabilités
-   Tests complets des services et des scrapers
-   Configuration sécurisée via variables d'environnement et GitHub Secrets

### Limites connues

-   L'API SoundCloud impose des limites de taux (rate limits)
-   Les résultats sont limités à 50 par défaut (max 200)
-   Certaines fonctionnalités nécessitent une authentification utilisateur
-   L'API nécessite des identifiants valides configurés correctement

### Ressources et Documentation SoundCloud

Pour plus d'informations sur l'API SoundCloud :

-   [Documentation officielle de l'API SoundCloud](https://developers.soundcloud.com/)
-   [Guide de l'API SoundCloud](https://developers.soundcloud.com/docs/api/guide)
-   [Référence de l'API SoundCloud](https://developers.soundcloud.com/docs/api/reference)
-   [Authentification OAuth 2.1](https://developers.soundcloud.com/docs/api/authentication)

**Configuration requise** :
1. Créer une application sur [SoundCloud Developers](https://developers.soundcloud.com/)
2. Obtenir le `Client ID` et `Client Secret`
3. Configurer les variables d'environnement `SOUNDCLOUD_CLIENT_ID` et `SOUNDCLOUD_CLIENT_SECRET`

**Note** : Le projet utilise le **Client Credentials Flow** qui ne nécessite pas d'URI de redirection.

## Flux de travail recommandé

Pour obtenir un profil SoundCloud complet avec ses réseaux sociaux :
1. Utiliser l'endpoint de recherche pour trouver les profils par nom
2. Les profils retournés incluent déjà leurs réseaux sociaux grâce à l'optimisation concurrente
3. Alternativement, utiliser directement l'endpoint profil avec un ID pour obtenir un profil spécifique

## Tests du projet

### Types de tests

- **Tests unitaires** : Couvrent les fonctionnalités individuelles des scrapers et services
  - Tests des scrapers SoundCloud : mockent les services
  - Tests des services SoundCloud : mockent les requêtes HTTP
  - Tests des scrapers Beatport : mockent BaseScraper.fetch
  - Tests des services génériques : retry, pagination

- **Tests d'intégration** : Vérifient l'interaction entre les différents composants
  - Tests des endpoints API complets
  - Validation des réponses API
  - Scénarios de bout en bout
  - Mockent au niveau des scrapers (interface publique)

### Architecture de test en couches

L'architecture de test respecte la séparation des responsabilités :

**Tests unitaires des scrapers :**
```python
@patch('app.services.soundcloud.soundcloud_api_service.SoundcloudApiService.get_user')
```

**Tests unitaires des services :**
```python
@patch('httpx.AsyncClient.request')
```

**Tests d'intégration :**
```python
@patch('app.scrapers.soundcloud.soundcloud_profile_scraper.SoundcloudProfileScraper.scrape')
```

### Optimisations des mocks et fixtures

- Suppression des fixtures inutilisées (`mock_social_links`)
- Utilisation ciblée de `mock_soundcloud_credentials` (pas d'`autouse=True`)
- Mocks optimisés sans redondances
- Structure cohérente pour tous les tests, facilitant la maintenance

### Exécution des tests

```bash
# Exécuter tous les tests
pytest

# Exécuter avec rapport de couverture
pytest --cov=app

# Exécuter uniquement les tests unitaires
pytest tests/unit

# Exécuter uniquement les tests d'intégration
pytest tests/integration
```

## Prochaines étapes

### Priorité haute

1. **Implémentation des scrapers restants** :

    - Bandcamp
    - Facebook
    - Instagram
    - Songstats

2. **Amélioration de la gestion des erreurs** :

    - Logging plus détaillé
    - Mécanismes de retry plus sophistiqués

### Priorité moyenne

1. **Documentation** :

    - Documentation plus détaillée des endpoints API
    - Exemples d'utilisation avec n8n

2. **Monitoring** :
    - Ajout de métriques (temps de réponse, taux d'erreur)
    - Intégration avec un système de monitoring

### Priorité basse

1. **Optimisations** :
    - Mise en cache des résultats fréquemment demandés
    - Parallélisation des requêtes

## Workflow de développement

1. **Développement local** :

    ```bash
    setup_venv.bat  # ou ./setup_venv.sh sur Linux/macOS
    ```

2. **Exécution des tests locaux** :

    ```bash
    # Lancer tous les tests
    pytest
    
    # Lancer les tests avec rapport de couverture
    pytest --cov=app
    ```

3. **Test avec Docker** :

    ```bash
    docker-compose up -d
    ```

4. **Déploiement** :
    - Push sur GitHub (branche master)
    - GitHub Actions exécute workflow deploy.yml qui déclenche:
      - test.yml pour les tests et le linting
      - build.yml pour la construction de l'image
    - Si tous les tests passent, déploiement automatique sur le VPS

## Intégration continue

Le projet utilise GitHub Actions pour l'automatisation des tests et du déploiement :

- **Workflow test.yml** : Exécute les tests et vérifications à chaque pull request
  - Exécution des tests unitaires et d'intégration
  - Génération de rapports de couverture de code
  - Peut être exécuté manuellement via manual-test.yml

- **Workflow build.yml** : Construction de l'image Docker
  - Construction de l'image Docker avec méta-données
  - Publication sur GitHub Container Registry

- **Workflow deploy.yml** : Orchestration du déploiement complet
  - Déclenché par un push sur la branche master
  - Appelle test.yml puis build.yml
  - Déploie sur le VPS via SSH si les étapes précédentes réussissent

## Notes techniques

-   L'API renvoie uniquement des données JSON, la persistance est gérée par l'appelant (n8n)
-   L'authentification se fait via une clé API dans le header `X-API-Key`
-   Les scrapers utilisent un mécanisme de retry avec backoff exponentiel
-   L'API est conçue pour être accessible uniquement en loopback sur le VPS
-   SoundCloud supporte CORS pour les requêtes cross-domain
-   Les erreurs de l'API SoundCloud sont gérées via les codes HTTP standards (400, 401, 403, etc.)
-   Les scrapers utilisent asyncio pour exécuter des requêtes en parallèle et améliorer les performances
-   Les profils et leurs réseaux sociaux sont récupérés simultanément grâce à l'exécution concurrente
-   Les tests utilisent pytest-mock et pytest-httpx pour simuler les requêtes externes
-   L'intégration continue garantit la qualité du code avant chaque déploiement

## Ressources

-   [Architecture détaillée](architecture.md)
-   [Documentation FastAPI](https://fastapi.tiangolo.com/)
-   [Documentation n8n](https://docs.n8n.io/)
-   [Documentation API SoundCloud](https://developers.soundcloud.com/docs/api/guide)
-   [Documentation pytest](https://docs.pytest.org/)
-   [GitHub Actions](https://docs.github.com/en/actions)
