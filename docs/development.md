# Journal de développement - techno-scraper

Ce document résume l'état actuel du projet, les fonctionnalités implémentées, et les prochaines étapes prévues.

## État actuel du projet (03/11/2025)

Le projet techno-scraper évolue d'une API REST FastAPI vers un serveur MCP (Model Context Protocol) pour intégration native avec les agents IA.

### Deux modes d'utilisation

- **[Nouveau] Serveur MCP** : Intégration directe avec Claude Desktop, n8n MCP
- **[Legacy] API REST FastAPI** : Maintenue temporairement, sera supprimée en Phase 4

### Plateformes supportées

- **Soundcloud** : Recherche de profils, données d'artistes, réseaux sociaux (REST + MCP ✅)
- **Beatport** : Recherche, releases avec facets de genres (REST uniquement, MCP Phase 2)
- **Bandcamp** : Recherche d'artistes et labels (REST uniquement, MCP Phase 3)

### Infrastructure technique

- Architecture en couches avec scrapers modulaires (partagée entre REST et MCP)
- **Serveur MCP** avec communication HTTP/SSE (Server-Sent Events)
- Authentification par clé API (REST uniquement)
- Tests unitaires et d'intégration complets (REST + MCP)
- CI/CD avec GitHub Actions

### Modifications récentes (03/11/2025) Migration MCP

-   **Implémentation du serveur MCP (Phase 1 - SoundCloud)**
    - Nouveau module `app/mcp/` avec serveur MCP complet
    - Deux tools SoundCloud fonctionnels :
      - `soundcloud_search_profiles` : Recherche d'artistes avec pagination
      - `soundcloud_get_profile` : Récupération de profil par ID
    - Architecture orientée tools (vs routes REST)
    - Communication HTTP/SSE (Server-Sent Events) sur port 8080
    - Configuration pour n8n MCP Server Trigger
    - Tests d'intégration MCP dans `tests/mcp/`
    - Documentation complète : `docs/mcp-usage.md`
    - Déploiement Docker avec Dockerfile.mcp
    - Mise à jour de `requirements.txt` : ajout de `mcp>=1.0.0`, upgrade `httpx>=0.27.1`
    - TODOs ajoutés dans le code legacy (routers, main.py) pour suppression Phase 4
    - Variables d'environnement lues depuis `.env` (pas de duplication dans config MCP)
    - Coexistence REST + MCP : même code métier (scrapers/services) partagé
    - Aucun breaking change : API REST toujours fonctionnelle

### Modifications précédentes (29/07/2025) Bandcamp

-   **Implémentation du scraper Bandcamp**
    - Nouveau scraper de recherche avec support des artistes et labels (`BandcampSearchScraper`)
    - Modèles de données spécialisés : `BandcampBandProfile`, `BandcampSearchResult`, `BandcampEntityType`
    - Router API complet avec endpoint `/bandcamp/search` et gestion d'erreurs
    - Utilitaires de mapping dédiés dans `bandcamp_mapping_utils.py`
    - Support de la pagination avec paramètre `page`
    - Filtrage par type d'entité (artistes/labels vs pistes)
    - Extraction des métadonnées : nom, URL, localisation, genre
    - Tests unitaires complets avec mocks pour `BaseScraper.fetch`
    - Tests d'intégration du router avec validation des réponses API
    - Architecture cohérente suivant les patterns établis du projet

### Modifications précédentes (25/07/2025) Beatport

-   **Amélioration du scraper Beatport releases avec extraction des facets**
    - Ajout de l'extraction des facets de genres depuis l'API Beatport
    - Nouveau modèle `BeatportReleasesResult` incluant releases et facets
    - Structure de retour enrichie : `{"releases": [...], "facets": {"fields": {"genre": [...]}}}`
    - Tests complets pour l'extraction des facets avec et sans données
    - Mise à jour des tests d'intégration pour la nouvelle structure de réponse

### Modifications précédentes (25/07/2025) Soundcloud

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

## Tests

Architecture de test en couches avec mocks appropriés selon le niveau. Voir [tests/README.md](../tests/README.md) pour plus de détails.

## Prochaines étapes

### Priorité haute - Migration MCP

**Plan de migration en 4 phases** :

1. **Phase 1 - SoundCloud MCP** ✅ (Terminé 03/11/2025)
   - Serveur MCP implémenté
   - Tools `soundcloud_search_profiles` et `soundcloud_get_profile`
   - Tests d'intégration MCP
   - Documentation complète

2. **Phase 2 - Beatport MCP** 🔄 (Prochaine étape)
   - Créer `app/mcp/tools/beatport_tools.py`
   - Implémenter les tools :
     - `beatport_search` : Recherche d'artistes/labels/releases/tracks
     - `beatport_get_releases` : Récupération de releases avec facets
   - Ajouter tests dans `tests/mcp/test_beatport_mcp_tools.py`
   - Mettre à jour `docs/mcp-usage.md`

3. **Phase 3 - Bandcamp MCP** 📅
   - Créer `app/mcp/tools/bandcamp_tools.py`
   - Implémenter le tool :
     - `bandcamp_search` : Recherche d'artistes et labels
   - Ajouter tests dans `tests/mcp/test_bandcamp_mcp_tools.py`
   - Mettre à jour `docs/mcp-usage.md`

4. **Phase 4 - Suppression REST API** 📅 (Après validation Phase 3)
   - Supprimer `app/main.py`
   - Supprimer `app/routers/` (soundcloud_router, beatport_router, bandcamp_router)
   - Supprimer `tests/integration/test_*_router.py`
   - Nettoyer `requirements.txt` (supprimer FastAPI, uvicorn si inutiles)
   - Mettre à jour `README.md` et `architecture.md`
   - Migration complète vers MCP uniquement

### Priorité moyenne

1. **Implémentation de nouveaux scrapers** :
   - Discogs (avec MCP tools)
   - Songstats (avec MCP tools)

2. **Amélioration de la gestion des erreurs** :
   - Logging plus détaillé
   - Mécanismes de retry plus sophistiqués

3. **Monitoring** :
   - Ajout de métriques (temps de réponse, taux d'erreur)
   - Intégration avec un système de monitoring

### Priorité basse

1. **Optimisations** :
   - Parallélisation des requêtes plus poussée
   - Cache pour les requêtes fréquentes

## Workflow de développement

1. **Local** : `setup_venv.bat` → `pytest` → `docker-compose up -d`
2. **Déploiement** : Push sur master → GitHub Actions (test → build → deploy)

## Ressources

### Documentation projet

- [Architecture détaillée](architecture.md) - Documentation technique complète avec section MCP
- [MCP Usage Guide](./mcp-usage.md) - Guide d'utilisation du serveur MCP
- [n8n MCP Setup](./n8n-mcp-setup.md) - Configuration MCP pour n8n
- [README.md](../README.md) - Vue d'ensemble et quick start
- [tests/README.md](../tests/README.md) - Guide des tests

### Documentation externe

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) - Documentation officielle MCP
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - SDK Python pour MCP
- [Documentation API SoundCloud](https://developers.soundcloud.com/docs/api/guide)
- [GitHub Actions](.github/workflows/) - Workflows CI/CD
