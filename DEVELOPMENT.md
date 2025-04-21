# Journal de développement - techno-scraper

Ce document résume l'état actuel du projet, les fonctionnalités implémentées, et les prochaines étapes prévues.

## État actuel du projet (21/04/2025)

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
-   Infrastructure de tests
    - Tests unitaires pour tous les scrapers
    - Tests d'intégration des endpoints API
    - Mocks pour les réponses externes

### Modifications récentes (21/04/2025)

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

L'API SoundCloud utilisée par notre scraper offre plusieurs fonctionnalités clés :

### Authentification

-   Support d'OAuth 2.1 avec deux flux principaux :
    -   Authorization Code Flow (pour actions au nom de l'utilisateur)
    -   Client Credentials Flow (pour accès aux ressources publiques uniquement)
-   Le scraper utilise principalement le Client Credentials Flow

### Fonctionnalités implémentées

-   Recherche de profils via l'endpoint `/search/users` avec paramètre `q`
-   Récupération de profils via l'endpoint `/users/{id}`
-   Récupération des réseaux sociaux via l'endpoint `/users/{id}/web-profiles`
-   Support de la pagination avec les paramètres `offset` et `limit`
-   Gestion des erreurs avec les codes HTTP appropriés
-   Exécution concurrente des requêtes pour de meilleures performances

### Limites connues

-   L'API SoundCloud impose des limites de taux (rate limits)
-   Les résultats sont limités à 50 par défaut (max 200)
-   Certaines fonctionnalités nécessitent une authentification utilisateur
-   L'API nécessite un `client_id` valide qui pourrait expirer

## Flux de travail recommandé

Pour obtenir un profil SoundCloud complet avec ses réseaux sociaux :
1. Utiliser l'endpoint de recherche pour trouver les profils par nom
2. Les profils retournés incluent déjà leurs réseaux sociaux grâce à l'optimisation concurrente
3. Alternativement, utiliser directement l'endpoint profil avec un ID pour obtenir un profil spécifique

## Tests du projet

### Types de tests

- **Tests unitaires** : Couvrent les fonctionnalités individuelles des scrapers et services
  - Tests des méthodes de récupération et de transformation des données
  - Validation des modèles de données
  - Tests des mécanismes de retries

- **Tests d'intégration** : Vérifient l'interaction entre les différents composants
  - Tests des endpoints API complets
  - Validation des réponses API
  - Scénarios de bout en bout

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

    - Beatport (recherche, releases)
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
