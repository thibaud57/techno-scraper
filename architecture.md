# Architecture du projet techno-scraper

Ce document décrit l'architecture du projet techno-scraper, une API FastAPI pour scraper des données de différents sites liés à la musique techno.

## Objectif du projet

Le projet techno-scraper vise à :

-   Scraper des données de sites musicaux (Soundcloud, Beatport, Bandcamp, Facebook, Instagram, Songstats)
-   Exposer ces données via une API FastAPI
-   Fonctionner en local et en production via Docker
-   Être utilisé par n8n sur un VPS

## Structure du projet

```
techno-scraper/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Point d'entrée de l'application FastAPI
│   ├── core/                    # Fonctionnalités centrales
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration de l'application
│   │   ├── security.py          # Gestion de l'authentification par clé API
│   │   └── errors.py            # Gestion des erreurs et exceptions
│   ├── models/                  # Modèles Pydantic pour la validation des données
│   │   ├── __init__.py
│   │   └── schemas.py           # Schémas de données communs
│   ├── routers/                 # Endpoints API
│   │   ├── __init__.py
│   │   ├── soundcloud.py        # Router pour Soundcloud
│   │   ├── beatport.py          # Router pour Beatport
│   │   ├── bandcamp.py          # Router pour Bandcamp
│   │   ├── facebook.py          # Router pour Facebook
│   │   ├── instagram.py         # Router pour Instagram
│   │   └── songstats.py         # Router pour Songstats
│   ├── services/                # Logique métier
│   │   ├── __init__.py
│   │   └── retry_service.py     # Service de retry avec backoff
│   └── scrapers/                # Modules de scraping
│       ├── __init__.py
│       ├── base.py              # Classe de base pour les scrapers
│       ├── soundcloud/          # Scraper pour Soundcloud
│       │   ├── __init__.py
│       │   ├── profile.py       # Scraping de profil
│       │   └── search.py        # Scraping de recherche
│       ├── beatport/            # Scraper pour Beatport
│       │   ├── __init__.py
│       │   ├── search.py        # Scraping de recherche
│       │   └── releases.py      # Scraping de releases
│       ├── bandcamp/            # Et ainsi de suite pour les autres sites...
│       ├── facebook/
│       ├── instagram/
│       └── songstats/
├── tests/                       # Tests unitaires et d'intégration
│   ├── __init__.py
│   ├── conftest.py              # Configuration des tests
│   ├── test_soundcloud.py
│   └── ...
├── .github/                     # Configuration GitHub
│   └── workflows/               # Workflows GitHub Actions
│       └── deploy.yml           # Workflow de déploiement
├── scripts/                     # Scripts utilitaires
│   └── deploy.sh                # Script de déploiement pour GitHub Actions
│   └── setup_venv.bat & .sh     # Script de config venv en local
├── .env.example                 # Exemple de variables d'environnement
├── .gitignore                   # Fichiers à ignorer par Git
├── Dockerfile                   # Configuration Docker
├── docker-compose.yml           # Configuration Docker Compose
├── requirements.txt             # Dépendances Python
└── README.md                    # Documentation du projet
```

## Diagramme d'architecture

```mermaid
graph TD
    Client[n8n] -->|API Request| API[FastAPI App]
    API -->|Authentication| Security[Security Middleware]
    Security -->|Routing| Routers[API Routers]
    Routers -->|Business Logic| Services[Services]
    Services -->|Data Extraction| Scrapers[Scrapers]
    Scrapers -->|HTTP Requests| ExternalSites[External Sites]
    ExternalSites -->|Response| Scrapers
    Scrapers -->|Parsed Data| Services
    Services -->|Formatted Response| Routers
    Routers -->|JSON Response| Client

    subgraph "API Layer"
        API
        Security
        Routers
    end

    subgraph "Business Layer"
        Services
    end

    subgraph "Data Layer"
        Scrapers
    end

    subgraph "External Resources"
        ExternalSites
    end

    subgraph "CI/CD Pipeline"
        GitHub[GitHub Repository] -->|Trigger| Actions[GitHub Actions]
        Actions -->|Build| DockerImage[Docker Image]
        DockerImage -->|Push| Registry[GitHub Container Registry]
        Registry -->|Pull| VPS[VPS Deployment]
    end
```

## Flux de données

```mermaid
sequenceDiagram
    participant n8n as n8n
    participant API as FastAPI
    participant Router as Router
    participant Service as Service
    participant Scraper as Scraper
    participant External as External Site

    n8n->>API: Request with API Key
    API->>API: Validate API Key
    API->>Router: Route Request
    Router->>Service: Process Request
    Service->>Scraper: Extract Data

    loop Retry Logic (limited)
        Scraper->>External: HTTP Request
        External->>Scraper: Response

        alt Success
            Scraper->>Service: Return Data
        else Temporary Error
            Scraper->>Scraper: Wait and Retry
        else Permanent Error
            Scraper->>Service: Return Detailed Error
        end
    end

    Service->>Router: Formatted Response
    Router->>API: JSON Response
    API->>n8n: Return JSON Data
```

## Flux de déploiement CI/CD

```mermaid
flowchart TD
    A[Push sur GitHub] --> B[Déclenchement du workflow GitHub Actions]
    B --> C[Construction de l'image Docker]
    C --> D[Tests automatisés]
    D --> E[Publication de l'image sur GitHub Container Registry]
    E --> F[Connexion SSH au VPS]
    F --> G[Déploiement via Docker Compose]
    G --> H[Vérification du déploiement]
```

## Détails des composants principaux

### 1. API Layer (FastAPI)

-   **main.py**: Point d'entrée de l'application, configuration des middlewares et des routers
-   **core/security.py**: Middleware d'authentification par clé API
-   **routers/**: Endpoints API organisés par site (un router par site)

### 2. Business Layer (Services)

-   **services/retry_service.py**: Gestion des retries avec backoff exponentiel
-   Logique métier pour transformer les données brutes en réponses API

### 3. Data Layer (Scrapers)

-   **scrapers/base.py**: Classe de base avec fonctionnalités communes
-   Scrapers spécifiques à chaque site, organisés par fonctionnalité

### 4. Configuration Docker

-   **Dockerfile**: Image Docker légère basée sur Python
-   **docker-compose.yml**: Configuration pour le déploiement local et en production

### 5. CI/CD avec GitHub Actions

-   **.github/workflows/deploy.yml**: Workflow de déploiement automatique
-   **scripts/deploy.sh**: Script de déploiement sur le VPS

## Sécurité

-   Authentification par clé API simple dans les headers
-   Accès limité au loopback pour usage local
-   Secrets stockés de manière sécurisée dans GitHub Actions

## Gestion des erreurs

-   Combinaison de retries limités avec backoff exponentiel
-   Erreurs explicites détaillées pour faciliter le débogage
-   Logging complet des erreurs et des tentatives

## Prochaines étapes

1. Implémentation des fichiers de base
2. Configuration de l'environnement Docker
3. Mise en place du CI/CD avec GitHub Actions
4. Développement des scrapers spécifiques à chaque site
