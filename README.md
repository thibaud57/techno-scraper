# Techno-scraper

API pour scraper des données de sites liés à la musique techno (Soundcloud, Beatport, Bandcamp, Facebook, Instagram, Songstats).

## 📋 Description

Techno-scraper est une API FastAPI qui permet de récupérer des données de différents sites liés à la musique techno. L'API est conçue pour être utilisée par n8n pour automatiser des workflows de récupération de données.

## 🚀 Fonctionnalités

-   Scraping de profils Soundcloud
-   Recherche sur Soundcloud
-   _(À venir)_ Scraping de profils Beatport
-   _(À venir)_ Recherche sur Beatport
-   _(À venir)_ Scraping de profils Bandcamp
-   _(À venir)_ Scraping de profils Facebook
-   _(À venir)_ Scraping de profils Instagram
-   _(À venir)_ Scraping de statistiques Songstats

## 🛠️ Technologies utilisées

-   [FastAPI](https://fastapi.tiangolo.com/) - Framework API moderne et performant
-   [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - Parsing HTML
-   [HTTPX](https://www.python-httpx.org/) - Client HTTP asynchrone
-   [Pydantic](https://pydantic-docs.helpmanual.io/) - Validation de données
-   [Docker](https://www.docker.com/) - Conteneurisation
-   [GitHub Actions](https://github.com/features/actions) - CI/CD

## 🔧 Installation

### Prérequis

-   [Docker](https://www.docker.com/get-started)
-   [Docker Compose](https://docs.docker.com/compose/install/)

### Installation locale

1. Cloner le dépôt :

    ```bash
    git clone https://github.com/votre-username/techno-scraper.git
    cd techno-scraper
    ```

2. Créer un fichier `.env` à partir du fichier `.env.example` :

    ```bash
    cp .env.example .env
    ```

3. Modifier le fichier `.env` avec vos propres valeurs.

4. Lancer l'application avec Docker Compose :

    ```bash
    docker-compose up -d
    ```

5. L'API est maintenant accessible à l'adresse [http://localhost:8000](http://localhost:8000)

### Installation sur un VPS

Le projet est configuré pour être déployé automatiquement sur un VPS via GitHub Actions. Pour configurer le déploiement automatique :

1. Forker le dépôt sur GitHub.

2. Configurer les secrets GitHub suivants :

    - `SSH_HOST` : Adresse IP de votre VPS
    - `SSH_USERNAME` : Nom d'utilisateur SSH
    - `SSH_PRIVATE_KEY` : Clé privée SSH
    - `SSH_PORT` : Port SSH (généralement 22)
    - `API_KEY` : Clé API pour l'authentification

3. Pousser vos modifications sur la branche `main` pour déclencher le déploiement automatique.

## 📚 Documentation API

Une fois l'application lancée, la documentation interactive de l'API est disponible aux adresses suivantes :

-   Swagger UI : [http://localhost:8000/docs](http://localhost:8000/docs)
-   ReDoc : [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🔐 Authentification

L'API utilise une authentification par clé API. Pour accéder aux endpoints, vous devez inclure la clé API dans l'en-tête `X-API-Key` de vos requêtes.

Exemple :

```bash
curl -X GET "http://localhost:8000/api/soundcloud/profile/techno-artist" -H "X-API-Key: your-api-key-here"
```

## 🧪 Tests

Pour exécuter les tests :

```bash
docker-compose run --rm techno-scraper pytest
```

## 📁 Structure du projet

```
techno-scraper/
├── app/                      # Code source de l'application
│   ├── core/                 # Fonctionnalités centrales
│   ├── models/               # Modèles de données
│   ├── routers/              # Endpoints API
│   ├── services/             # Services
│   └── scrapers/             # Modules de scraping
├── tests/                    # Tests
├── .github/                  # Configuration GitHub
├── scripts/                  # Scripts utilitaires
├── Dockerfile                # Configuration Docker
├── docker-compose.yml        # Configuration Docker Compose
└── requirements.txt          # Dépendances Python
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
