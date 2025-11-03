# Configuration MCP avec n8n

Guide pour intégrer le serveur MCP techno-scraper avec n8n.

## 🎯 Prérequis

- n8n installé (version avec support MCP)
- Python 3.10+ avec les dépendances installées
- Variables d'environnement SoundCloud configurées

## 📦 Installation

### 1. Préparer le serveur MCP

```bash
# Cloner et configurer le projet
cd /path/to/techno-scraper
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env et ajouter vos clés SoundCloud
```

### 2. Tester le serveur MCP

```bash
# Vérifier que le serveur démarre correctement
python -m app.mcp.server
```

Si tout fonctionne, vous devriez voir des logs sans erreur.

## 🔧 Configuration n8n

### Option 1 : Configuration globale

1. Créer un fichier de configuration MCP pour n8n :

```json
{
  "mcpServers": {
    "techno-scraper": {
      "command": "python",
      "args": ["-m", "app.mcp.server"],
      "cwd": "/path/to/techno-scraper",
      "env": {
        "SOUNDCLOUD_CLIENT_ID": "your-client-id",
        "SOUNDCLOUD_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

2. Placer ce fichier dans le répertoire de configuration n8n

### Option 2 : Configuration par workflow

Vous pouvez configurer le serveur MCP directement dans un workflow n8n en utilisant un nœud "MCP Server".

## 🛠️ Utilisation dans n8n

### Exemple de workflow : Recherche SoundCloud

1. **Nœud déclencheur** : Webhook, Schedule, ou Manual
2. **Nœud MCP Tool** :
   - Serveur : `techno-scraper`
   - Tool : `soundcloud_search_profiles`
   - Arguments :
     ```json
     {
       "query": "{{ $json.artist_name }}",
       "limit": 10,
       "page": 1
     }
     ```
3. **Nœud traitement** : Traiter les résultats JSON

### Exemple de workflow : Récupération de profil

1. **Nœud déclencheur**
2. **Nœud MCP Tool** :
   - Serveur : `techno-scraper`
   - Tool : `soundcloud_get_profile`
   - Arguments :
     ```json
     {
       "user_id": {{ $json.user_id }}
     }
     ```
3. **Nœud traitement**

## 🔍 Debugging

### Vérifier les logs n8n

Les logs du serveur MCP apparaîtront dans les logs n8n. Vérifiez :
- Les erreurs de connexion
- Les problèmes d'authentification SoundCloud
- Les erreurs de scraping

### Tester manuellement

Avant d'utiliser dans n8n, testez le serveur MCP :

```bash
# Test manuel avec une requête JSON-RPC
echo '{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "soundcloud_search_profiles",
    "arguments": {
      "query": "Carl Cox",
      "limit": 10
    }
  },
  "id": 1
}' | python -m app.mcp.server
```

## 📊 Exemple de workflow complet

### Workflow : Veille artistes SoundCloud

```
1. Schedule (tous les jours à 9h)
   ↓
2. Get Artists from Database
   ↓
3. Loop Over Artists
   ↓
4. MCP Tool: soundcloud_search_profiles
   - query: {{ $json.artist_name }}
   ↓
5. Filter New Results
   ↓
6. MCP Tool: soundcloud_get_profile (pour chaque nouveau)
   - user_id: {{ $json.profile.id }}
   ↓
7. Save to Database
   ↓
8. Send Notification
```

## 🚀 Déploiement sur VPS

### Avec Docker

Si vous déployez n8n sur un VPS avec Docker :

1. Créer un `docker-compose.yml` incluant le serveur MCP :

```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your-password
    volumes:
      - n8n_data:/home/node/.n8n
      - ./mcp_config.json:/home/node/.n8n/mcp_config.json
      - ./techno-scraper:/app/techno-scraper
    depends_on:
      - techno-scraper-mcp

  techno-scraper-mcp:
    build: ./techno-scraper
    environment:
      - SOUNDCLOUD_CLIENT_ID=${SOUNDCLOUD_CLIENT_ID}
      - SOUNDCLOUD_CLIENT_SECRET=${SOUNDCLOUD_CLIENT_SECRET}

volumes:
  n8n_data:
```

2. Démarrer les services :

```bash
docker-compose up -d
```

## 🔒 Sécurité

- Utilisez des variables d'environnement pour les secrets
- Ne commitez jamais les clés API dans git
- Limitez l'accès au serveur n8n (authentification)
- Utilisez HTTPS en production

## 📚 Ressources

- [Documentation n8n](https://docs.n8n.io/)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [techno-scraper MCP_USAGE.md](./MCP_USAGE.md)
