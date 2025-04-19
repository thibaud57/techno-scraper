# Journal de développement - techno-scraper

Ce document résume l'état actuel du projet, les fonctionnalités implémentées, et les prochaines étapes prévues.

## État actuel du projet (19/04/2025)

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
-   Modèles de données pour les résultats et la pagination
-   Support des scrapers modulaires avec BaseScraper
-   Service de retries
-   Scraper pour Soundcloud
    - Recherche de profils
    - Profil (par ID)
    - Réseaux sociaux

### Modifications récentes (19/04/2025)

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
-   SoundCloud supporte CORS pour les requêtes cross-domain
-   Les erreurs de l'API SoundCloud sont gérées via les codes HTTP standards (400, 401, 403, etc.)
-   Les scrapers utilisent asyncio pour exécuter des requêtes en parallèle et améliorer les performances
-   Les profils et leurs réseaux sociaux sont récupérés simultanément grâce à l'exécution concurrente

## Ressources

-   [Architecture détaillée](architecture.md)
-   [Documentation FastAPI](https://fastapi.tiangolo.com/)
-   [Documentation n8n](https://docs.n8n.io/)
-   [Documentation API SoundCloud](https://developers.soundcloud.com/docs/api/guide)
