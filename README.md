# Techno-scraper

API FastAPI pour scraper des données de sites musicaux (Soundcloud, Beatport, Bandcamp, etc.).

## 📋 Description

Techno-scraper permet de récupérer automatiquement des données depuis différentes plateformes musicales. Le projet propose deux modes d'utilisation :
- **API REST** : Interface FastAPI classique (en cours de migration)
- **Serveur MCP** : Intégration directe avec des agents IA (Claude Desktop, n8n)

## 🎯 Mode MCP (Nouveau !)

Le projet supporte maintenant le **Model Context Protocol (MCP)** d'Anthropic pour une intégration native avec les agents IA.

**Avantages MCP** :
- Intégration directe dans Claude Desktop
- Pas besoin de gérer des endpoints HTTP
- Communication sécurisée via stdio
- Typage fort des paramètres

**Quick Start MCP** :
```bash
# Lancer le serveur MCP
python -m app.mcp.server
```

📖 **Documentation complète** : [MCP_USAGE.md](./MCP_USAGE.md) | [N8N_MCP_SETUP.md](./N8N_MCP_SETUP.md)

## 🚀 Fonctionnalités

- **Soundcloud** : Recherche de profils, données d'artistes, réseaux sociaux
- **Beatport** : Recherche d'artistes/labels/releases, extraction avec facets
- **Bandcamp** : Recherche d'artistes et labels avec pagination
- **À venir** : Discogs, Songstats

## 🛠️ Technologies

FastAPI, BeautifulSoup4, HTTPX, Pydantic, Docker, pytest

## ⚡ Démarrage rapide

1. **Docker (recommandé)** :
   ```bash
   git clone <repo-url>
   cd techno-scraper
   cp .env.example .env  # Configurer vos clés API
   docker-compose up -d
   ```

2. **Local** :
   ```bash
   scripts/setup_venv.bat  # Windows
   ./scripts/setup_venv.sh # Linux/macOS
   python app/main.py
   ```

3. **Accès** : [http://localhost:8000](http://localhost:8000)

## ⚙️ Configuration

### Variables d'environnement requises

Créez un fichier `.env` à partir de `.env.example` et configurez :

```bash
# Authentification API
API_KEY=your-secure-api-key-here

# SoundCloud (requis pour les scrapers SoundCloud)
SOUNDCLOUD_CLIENT_ID=your-soundcloud-client-id
SOUNDCLOUD_CLIENT_SECRET=your-soundcloud-client-secret
```

### Configuration SoundCloud

1. Créez une application sur [SoundCloud Developers](https://developers.soundcloud.com/)
2. Obtenez votre `Client ID` et `Client Secret`
3. Ajoutez-les à votre fichier `.env`

Le projet utilise le **Client Credentials Flow** OAuth 2.1 (pas besoin d'URI de redirection).

## 📖 Utilisation

**Documentation interactive** : [http://localhost:8000/docs](http://localhost:8000/docs)

**Authentification** : Header `X-API-Key`

**Exemple** :
```bash
curl -H "X-API-Key: your-key" "http://localhost:8000/soundcloud/search?query=artist"
```

## 🧪 Tests

```bash
pytest                    # Tous les tests
pytest --cov=app         # Avec couverture
scripts/run_tests.bat    # Windows
./scripts/run_tests.sh   # Linux/macOS
```

Voir [tests/README.md](tests/README.md) pour plus de détails.

## 📚 Documentation complète

- **[docs/architecture.md](docs/architecture.md)** - Architecture technique détaillée
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Journal de développement et état du projet
- **[tests/README.md](tests/README.md)** - Guide des tests

## 🤝 Contribution

Les contributions sont bienvenues ! Consultez [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) pour le workflow de développement.

## 📄 Licence

MIT