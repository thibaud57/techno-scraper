# Techno-Scraper MCP Server

Ce document décrit comment utiliser le serveur MCP (Model Context Protocol) de techno-scraper pour intégrer les fonctionnalités de scraping dans des agents IA comme Claude Desktop ou n8n.

## 🎯 Qu'est-ce que MCP ?

MCP (Model Context Protocol) est un protocole standardisé créé par Anthropic pour permettre aux agents IA d'interagir avec des outils externes de manière structurée. Le serveur MCP expose des outils via HTTP/SSE (Server-Sent Events) pour une communication temps-réel avec les agents IA.

## 📦 Installation

### Prérequis

```bash
# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env et ajouter vos clés API SoundCloud
```

### Variables d'environnement requises

```bash
SOUNDCLOUD_CLIENT_ID=your-soundcloud-client-id
SOUNDCLOUD_CLIENT_SECRET=your-soundcloud-client-secret
MCP_PORT=8080  # Port du serveur MCP (optionnel, 8080 par défaut)
```

## 🔧 Configuration

### Lancement du serveur MCP

Le serveur MCP utilise le transport HTTP/SSE et écoute par défaut sur le port 8080 :

```bash
# Lancement local
python -m app.mcp

# Avec Docker
docker-compose -f docker-compose.dokploy.yml up techno-scraper-mcp

# Le serveur est accessible sur http://localhost:8080/sse
```

### Pour n8n

Le serveur MCP est conçu pour fonctionner avec le node **MCP Server Trigger** de n8n.

#### Configuration dans n8n

1. Dans votre workflow n8n, ajoutez un node **MCP Server Trigger**
2. Configurez l'URL du serveur MCP :
   - **Développement local** : `http://techno-scraper-mcp:8080/sse` (via Docker network)
   - **Production** : `http://techno-scraper-mcp:8080/sse` (via Docker network)
3. n8n expose ensuite publiquement via : `https://n8n.empiricmind.fr/mcp/techno-scraper-mcp/sse`

#### Architecture réseau

```
Agent IA (Claude/n8n workflow)
    ↓
n8n MCP Server Trigger (https://n8n.empiricmind.fr/mcp/techno-scraper-mcp/sse)
    ↓
techno-scraper-mcp container (http://techno-scraper-mcp:8080/sse)
    ↓
SoundCloud API
```

#### Variables d'environnement dans Dokploy

Dans la configuration Dokploy, configurez :
```bash
SOUNDCLOUD_CLIENT_ID=your-soundcloud-client-id
SOUNDCLOUD_CLIENT_SECRET=your-soundcloud-client-secret
MCP_PORT=8080  # Optionnel, 8080 par défaut
```

### Pour Claude Desktop (stdio local)

**Note** : Le serveur MCP actuel utilise HTTP/SSE et n'est pas compatible avec Claude Desktop en mode stdio local. Pour une utilisation avec Claude Desktop, une configuration client HTTP sera nécessaire (à venir).

## 🛠️ Tools disponibles

### 1. soundcloud_search_profiles

Recherche des profils d'artistes sur SoundCloud par nom ou mot-clé.

**Paramètres** :
- `query` (string, requis) : Nom de l'artiste ou mot-clé de recherche
- `page` (integer, optionnel) : Numéro de page pour la pagination (défaut: 1)
- `limit` (integer, optionnel) : Nombre de résultats par page - 10, 20 ou 50 (défaut: 10)

**Retour** :
```json
{
  "total_results": 150,
  "page": 1,
  "limit": 10,
  "profiles": [
    {
      "id": 123456,
      "name": "Artist Name",
      "url": "https://soundcloud.com/artist-name",
      "bio": "Artist biography",
      "location": "City, Country",
      "followers_count": 10000,
      "social_links": [
        {
          "platform": "facebook",
          "url": "https://facebook.com/artistname"
        }
      ]
    }
  ]
}
```

**Exemple d'utilisation dans Claude** :
```
Peux-tu chercher des profils SoundCloud pour "Carl Cox" ?
```

### 2. soundcloud_get_profile

Récupère les informations détaillées d'un profil SoundCloud spécifique par son ID utilisateur.

**Paramètres** :
- `user_id` (integer, requis) : ID utilisateur SoundCloud

**Retour** :
```json
{
  "id": 123456,
  "name": "Artist Name",
  "url": "https://soundcloud.com/artist-name",
  "bio": "Artist biography",
  "location": "City, Country",
  "followers_count": 10000,
  "social_links": [
    {
      "platform": "instagram",
      "url": "https://instagram.com/artistname"
    }
  ]
}
```

**Exemple d'utilisation dans Claude** :
```
Peux-tu récupérer le profil SoundCloud de l'utilisateur avec l'ID 12345678 ?
```

### 3. beatport_search

Recherche des labels, artistes, tracks ou releases sur Beatport par nom ou mot-clé.

**Paramètres** :
- `query` (string, requis) : Nom du label, artiste ou mot-clé de recherche
- `page` (integer, optionnel) : Numéro de page pour la pagination (défaut: 1)
- `limit` (integer, optionnel) : Nombre de résultats par page - 10, 25 ou 50 (défaut: 10)
- `entity_type` (string, optionnel) : Filtre par type - "artist", "label", "track", "release", ou null pour tous (défaut: null)

**Retour** :
```json
{
  "total_results": 25,
  "page": 1,
  "limit": 10,
  "artists": [
    {
      "id": 12345,
      "name": "Artist Name",
      "url": "https://www.beatport.com/artist/artist-name/12345",
      "avatar_url": "https://geo-media.beatport.com/image.jpg"
    }
  ],
  "labels": [
    {
      "id": 22038,
      "name": "Drumzone Records",
      "url": "https://www.beatport.com/label/drumzone-records/22038",
      "avatar_url": "https://geo-media.beatport.com/image.jpg"
    }
  ],
  "tracks": [],
  "releases": []
}
```

**Exemple d'utilisation** :
```
Peux-tu chercher le label "Afterlife" sur Beatport ?
```

### 4. beatport_get_label_releases

Récupère les releases d'un label Beatport avec les statistiques de genres (facets).

**Paramètres** :
- `entity_slug` (string, requis) : Slug du label (ex: "drumzone-records")
- `entity_id` (string, requis) : ID du label (ex: "22038")
- `page` (integer, optionnel) : Numéro de page (défaut: 1)
- `limit` (integer, optionnel) : Nombre de résultats par page - 10, 25 ou 50 (défaut: 25)
- `start_date` (string, optionnel) : Date de début au format YYYY-MM-DD (ex: "2024-01-15")

**Retour** :
```json
{
  "releases": [
    {
      "id": 456789,
      "name": "Release Name",
      "url": "https://www.beatport.com/release/...",
      "artists": [{"id": 123, "name": "Artist Name"}],
      "label": {"id": 22038, "name": "Drumzone Records"},
      "publish_date": "2024-06-15"
    }
  ],
  "facets": {
    "fields": {
      "genre": [
        {"name": "Techno (Peak Time / Driving)", "count": 32},
        {"name": "Deep House", "count": 5}
      ]
    }
  }
}
```

**Exemple d'utilisation** :
```
Peux-tu récupérer les releases du label Drumzone Records (slug: drumzone-records, id: 22038) depuis le 1er janvier 2024 ?
```

### 5. bandcamp_search

Recherche des artistes, labels sur Bandcamp par nom ou mot-clé.

**Paramètres** :
- `query` (string, requis) : Nom de l'artiste, label ou mot-clé de recherche
- `page` (integer, optionnel) : Numéro de page pour la pagination (défaut: 1)
- `entity_type` (string, optionnel) : Type de recherche - "bands" pour artistes/labels ou "tracks" pour pistes (défaut: "bands")

**Retour** :
```json
{
  "bands": [
    {
      "id": 123456,
      "name": "Label Name",
      "url": "https://labelname.bandcamp.com",
      "avatar_url": "https://f4.bcbits.com/img/...",
      "location": "Berlin, Germany",
      "genre": "Electronic"
    }
  ],
  "tracks": []
}
```

**Exemple d'utilisation** :
```
Peux-tu chercher le label "Nous'klaer Audio" sur Bandcamp ?
```

## 🧪 Tests

### Tester le serveur MCP localement

```bash
# Lancer le serveur MCP
python -m app.mcp

# Le serveur écoute sur http://localhost:8080/sse
# Vérifier que le serveur répond
curl -f http://localhost:8080/sse
```

### Exécuter les tests unitaires

```bash
# Tests des tools MCP
pytest tests/mcp/test_soundcloud_mcp_tools.py -v

# Tous les tests
pytest
```

## 🔍 Debugging

### Logs

Le serveur MCP log les informations importantes. Les logs apparaissent dans la sortie standard :

```bash
# Lancer avec des logs détaillés
python -m app.mcp

# Exemple de logs :
# 2025-01-03 10:30:45 - INFO - Starting MCP server on http://0.0.0.0:8080/sse
```

### Vérifier que le serveur fonctionne

```bash
# Le serveur doit démarrer sans erreur et afficher :
python -m app.mcp
# INFO:     Started server process [12345]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8080

# Healthcheck
curl -f http://localhost:8080/sse

# Logs Docker
docker logs techno-scraper-mcp
```

## 📋 Roadmap

### Phase 1 : SoundCloud ✅
- [x] Tool `soundcloud_search_profiles`
- [x] Tool `soundcloud_get_profile`
- [x] Tests d'intégration
- [x] Documentation

### Phase 2 : Beatport ✅
- [x] Tool `beatport_search`
- [x] Tool `beatport_get_label_releases`
- [x] Integration avec n8n MCP Client
- [x] Documentation

### Phase 3 : Bandcamp ✅
- [x] Tool `bandcamp_search`
- [x] Integration avec n8n MCP Client
- [x] Documentation
- [ ] Tests d'intégration MCP (optionnel)

### Phase 4 : Nettoyage
- [ ] Suppression de l'API REST (routers/)
- [ ] Mise à jour de la documentation
- [ ] Migration complète vers MCP

## 🔒 Sécurité

- Les clés API sont passées via variables d'environnement
- Le serveur MCP est accessible uniquement via le réseau Docker interne (pas d'exposition publique directe)
- n8n gère l'exposition publique et l'authentification
- Pour une utilisation en production, utiliser des secrets managers (ex: Doppler, Vault)

## 🆘 Support

Pour toute question ou problème :
1. Vérifier les logs du serveur MCP
2. Vérifier que les variables d'environnement sont correctement configurées
3. Tester les scrapers unitairement avant de tester via MCP
4. Consulter la documentation MCP d'Anthropic : https://modelcontextprotocol.io/

## 📚 Ressources

- [Documentation MCP officielle](https://modelcontextprotocol.io/)
- [SDK Python MCP](https://github.com/modelcontextprotocol/python-sdk)
- [Documentation SoundCloud API](https://developers.soundcloud.com/)
