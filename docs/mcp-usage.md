# Techno-Scraper MCP Server

Ce document décrit comment utiliser le serveur MCP (Model Context Protocol) de techno-scraper pour intégrer les fonctionnalités de scraping dans des agents IA comme Claude Desktop ou n8n.

## 🎯 Qu'est-ce que MCP ?

MCP (Model Context Protocol) est un protocole standardisé créé par Anthropic pour permettre aux agents IA d'interagir avec des outils externes de manière structurée. Au lieu d'appeler une API REST classique, l'agent communique directement avec le serveur MCP via JSON-RPC.

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
```

## 🔧 Configuration

### Pour Claude Desktop

1. Localisez votre fichier de configuration Claude Desktop :
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Ajoutez la configuration du serveur MCP :

```json
{
  "mcpServers": {
    "techno-scraper": {
      "command": "python",
      "args": [
        "-m",
        "app.mcp.server"
      ],
      "cwd": "/path/to/techno-scraper",
      "env": {
        "SOUNDCLOUD_CLIENT_ID": "your-soundcloud-client-id",
        "SOUNDCLOUD_CLIENT_SECRET": "your-soundcloud-client-secret"
      }
    }
  }
}
```

3. Remplacez `/path/to/techno-scraper` par le chemin absolu vers votre répertoire techno-scraper

4. Redémarrez Claude Desktop

### Pour n8n

Documentation à venir pour l'intégration avec n8n.

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

## 🧪 Tests

### Tester le serveur MCP localement

```bash
# Lancer le serveur MCP en mode standalone
python -m app.mcp.server
```

Le serveur attend des entrées JSON-RPC sur stdin et retourne les résultats sur stdout.

### Exécuter les tests unitaires

```bash
# Tests des tools MCP
pytest tests/mcp/test_soundcloud_mcp_tools.py -v

# Tous les tests
pytest
```

## 🔍 Debugging

### Logs

Le serveur MCP log les informations importantes. Pour augmenter le niveau de verbosité :

```python
# Dans app/mcp/server.py, modifier le niveau de logging
logging.basicConfig(
    level=logging.DEBUG,  # Au lieu de INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
```

### Vérifier que le serveur fonctionne

```bash
# Le serveur doit démarrer sans erreur
python -m app.mcp.server

# Dans un autre terminal, vous pouvez envoyer une requête JSON-RPC
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | python -m app.mcp.server
```

## 📋 Roadmap

### Phase 1 : SoundCloud ✅
- [x] Tool `soundcloud_search_profiles`
- [x] Tool `soundcloud_get_profile`
- [x] Tests d'intégration
- [x] Documentation

### Phase 2 : Beatport (À venir)
- [ ] Tool `beatport_search`
- [ ] Tool `beatport_get_releases`
- [ ] Tests d'intégration

### Phase 3 : Bandcamp (À venir)
- [ ] Tool `bandcamp_search`
- [ ] Tests d'intégration

### Phase 4 : Nettoyage
- [ ] Suppression de l'API REST (routers/)
- [ ] Mise à jour de la documentation
- [ ] Migration complète vers MCP

## 🔒 Sécurité

- Les clés API sont passées via variables d'environnement
- Le serveur MCP ne nécessite pas d'authentification externe (communication via stdio)
- Pour une utilisation en production, considérer l'utilisation de secrets managers

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
