# Techno-scraper

API pour scraper des données de sites liés à la musique techno (Soundcloud, Beatport, Bandcamp, Facebook, Instagram, Songstats).

## 📋 Description

Techno-scraper est une API FastAPI qui permet de récupérer des données de différents sites liés à la musique techno. L'API est conçue pour être utilisée par n8n pour automatiser des workflows de récupération de données.

## 🚀 Fonctionnalités

### Soundcloud
- **Recherche profils** : Extraction des informations détaillées des profils d'artistes avec authentification OAuth 2.1
- **Profil par id** : Extraction des données d'un profil en recherchant par son id
- **Réseaux sociaux** : Récupération des liens vers les plateformes externes (Facebook, Instagram, sites web personnels, etc.)

### Beatport
- **Recherche** : Extraction de données pour les artistes, labels, releases et tracks
- **Releases par artiste/label** : Récupération des sorties musicales d'un artiste ou d'un label avec filtrage par date et pagination

### À venir
- **Bandcamp** : Informations sur les artistes et leurs albums
- **Facebook/Instagram** : Extraction de données des réseaux sociaux
- **Songstats** : Récupération des statistiques de streaming

## 🛠️ Technologies utilisées

-   [FastAPI](https://fastapi.tiangolo.com/) - Framework API moderne et performant
-   [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - Parsing HTML
-   [HTTPX](https://www.python-httpx.org/) - Client HTTP asynchrone
-   [Pydantic](https://pydantic-docs.helpmanual.io/) - Validation de données
-   [asyncio](https://docs.python.org/3/library/asyncio.html) - Programmation asynchrone pour requêtes concurrentes
-   [pytest](https://docs.pytest.org/) - Framework de test
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
    - `SOUNDCLOUD_CLIENT_ID` : Client ID de votre application SoundCloud
    - `SOUNDCLOUD_CLIENT_SECRET` : Client Secret de votre application SoundCloud

3. Pousser vos modifications sur la branche `main` pour déclencher le déploiement automatique.

## 📚 Documentation API

Une fois l'application lancée, la documentation interactive de l'API est disponible aux adresses suivantes :

-   Swagger UI : [http://localhost:8000/docs](http://localhost:8000/docs)
-   ReDoc : [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🔐 Authentification

L'API utilise une authentification par clé API. Pour accéder aux endpoints, vous devez inclure la clé API dans l'en-tête `X-API-Key` de vos requêtes.

Exemple :

```bash
curl -X GET "http://localhost:8000/api/soundcloud/profile/123456" -H "X-API-Key: your-api-key-here"
```

## 🧪 Tests

Le projet dispose d'une suite complète de tests unitaires et d'intégration. Pour plus de détails, consultez le [README.md des tests](tests/README.md).

Pour exécuter tous les tests :

```bash
# Sur Windows
.\scripts\run_tests.bat

# Sur Linux/MacOS
./scripts/run_tests.sh

# Avec Docker
docker-compose run --rm techno-scraper pytest
```

Pour exécuter les tests avec couverture de code :

```bash
pytest --cov=app
```

## 🔄 Intégration continue

Le projet utilise GitHub Actions pour l'automatisation des tests et du déploiement :

- **Workflow test.yml** : Exécuté automatiquement lors des pull requests
  - Exécution des tests unitaires et d'intégration
  - Génération de rapports de couverture de code
  - Peut être déclenché manuellement via manual-test.yml

- **Workflow build.yml** : Construction de l'image Docker
  - Construction de l'image avec tags appropriés
  - Publication sur GitHub Container Registry

- **Workflow deploy.yml** : Orchestration du déploiement complet
  - Déclenché par un push sur la branche master
  - Appelle test.yml puis build.yml en séquence
  - Déploie sur le VPS via SSH si les étapes précédentes réussissent

Pour plus de détails sur les workflows, consultez le dossier `.github/workflows/`.

## 📁 Structure du projet

```
techno-scraper/
├── app/                      # Code source de l'application
│   ├── core/                 # Fonctionnalités centrales
│   ├── models/               # Modèles de données
│   ├── routers/              # Endpoints API
│   ├── services/             # Services (authentification, API, pagination, retry)
│   │   └── soundcloud/       # Services SoundCloud dédiés
│   └── scrapers/             # Modules de scraping
│       └── soundcloud/       # Scrapers SoundCloud avec architecture moderne
├── tests/                    # Tests unitaires et d'intégration (103 tests)
│   ├── conftest.py           # Configuration des tests
│   ├── integration/          # Tests d'intégration (33 tests)
│   ├── mocks/                # Mocks optimisés pour les tests
│   ├── scrapers/             # Tests des scrapers (46 tests)
│   │   └── soundcloud/       # Tests SoundCloud mis à jour
│   └── services/             # Tests des services (24 tests)
│       └── soundcloud/       # Tests des services SoundCloud
├── .github/                  # Configuration GitHub
├── scripts/                  # Scripts utilitaires
├── Dockerfile                # Configuration Docker
├── docker-compose.yml        # Configuration Docker Compose
└── requirements.txt          # Dépendances Python
```

## 📚 Ressources et Documentation

### API SoundCloud
- [Documentation officielle de l'API SoundCloud](https://developers.soundcloud.com/)
- [Guide de l'API SoundCloud](https://developers.soundcloud.com/docs/api/guide)
- [Référence de l'API SoundCloud](https://developers.soundcloud.com/docs/api/reference)
- [Authentification OAuth 2.1](https://developers.soundcloud.com/docs/api/authentication)

### Configuration SoundCloud
Pour utiliser l'intégration SoundCloud, vous devez :
1. Créer une application sur [SoundCloud Developers](https://developers.soundcloud.com/)
2. Obtenir votre `Client ID` et `Client Secret`
3. Configurer ces identifiants dans vos variables d'environnement

Le projet utilise le **Client Credentials Flow** d'OAuth 2.1 pour l'authentification, permettant l'accès aux ressources publiques de SoundCloud sans intervention utilisateur.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.