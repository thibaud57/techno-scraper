# Journal de développement - techno-scraper

Ce document résume l'état actuel du projet, les fonctionnalités implémentées, et les prochaines étapes prévues.

## État actuel du projet (17/04/2025)

Le projet techno-scraper est une API FastAPI conçue pour scraper des données de différents sites liés à la musique techno (Soundcloud, Beatport, Bandcamp, Facebook, Instagram, Songstats). L'API est destinée à être utilisée par n8n pour automatiser des workflows de récupération de données.

### Structure implémentée

-   Architecture en couches (routers, services, models, scrapers)
-   Configuration Docker pour le développement local et le déploiement
-   Configuration GitHub Actions pour le déploiement automatique sur VPS
-   Scripts utilitaires pour le développement local

### Fonctionnalités implémentées

-   Structure de base de l'application FastAPI
-   Authentification par clé API
-   Gestion des erreurs et des retries
-   Exemple de scraper pour les profils Soundcloud

### Problèmes résolus

-   Correction d'une erreur de dépendance FastAPI (`AssertionError: A parameter-less dependency must have a callable dependency`)
    -   Solution : Utilisation correcte de `Depends(get_api_key)` au lieu de `Depends(api_key_auth)`

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

3. **Tests** :
    - Tests unitaires pour les scrapers
    - Tests d'intégration pour les endpoints API

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

    ```
    setup_venv.bat  # ou ./setup_venv.sh sur Linux/macOS
    ```

2. **Test avec Docker** :

    ```
    docker-compose up -d
    ```

3. **Déploiement** :
    - Push sur GitHub
    - GitHub Actions déploie automatiquement sur le VPS

## Notes techniques

-   L'API renvoie uniquement des données JSON, la persistance est gérée par l'appelant (n8n)
-   L'authentification se fait via une clé API dans le header `X-API-Key`
-   Les scrapers utilisent un mécanisme de retry avec backoff exponentiel
-   L'API est conçue pour être accessible uniquement en loopback sur le VPS

## Ressources

-   [Architecture détaillée](architecture.md)
-   [Documentation FastAPI](https://fastapi.tiangolo.com/)
-   [Documentation n8n](https://docs.n8n.io/)
