# Prompts n8n pour extraction de données labels musicaux

Ce dossier contient tous les prompts et configurations pour le workflow n8n d'extraction automatique d'informations sur les labels musicaux.

## 📁 Fichiers

### Prompts Agents

- **`agent-soundcloud-system-prompt.md`** : Prompt système pour l'agent SoundCloud
  - Recherche et sélection du profil pertinent
  - Extraction pays, email demo, followers, liens sociaux

- **`agent-beatport-system-prompt.md`** : Prompt système pour l'agent Beatport
  - Recherche du label et extraction releases sur 1 an
  - Calcul genre, isActive, isOpenNew

### Output Parsers

- **`output-parser-soundcloud.json`** : JSON Schema pour valider l'output de l'agent SoundCloud
- **`output-parser-beatport.json`** : JSON Schema pour valider l'output de l'agent Beatport

### Code Nodes

- **`code-node-merge.js`** : Code JavaScript pour fusionner les outputs des 2 agents

## 🏗️ Architecture du workflow n8n

```
Google Sheet Trigger
    ↓
┌────────┴─────────┐
│                  │
↓                  ↓
Agent             Agent
SoundCloud        Beatport
(MCP Client)      (MCP Client)
│                  │
└────────┬─────────┘
         ↓
    Code Node (merge)
         ↓
   Google Sheet Update
```

## 📋 Configuration n8n

### Agent SoundCloud

1. **Type de node** : AI Agent
2. **MCP Client Configuration** :
   - Transport Type : `SSE`
   - URL : `http://techno-scraper-mcp:8080/sse`
   - Tools : Limiter à `soundcloud_*`
3. **User Prompt** :
   ```
   Nom du label: {{ $json.name }}
   ```
4. **System Prompt** : Copier le contenu de `agent-soundcloud-system-prompt.md`
5. **Output Parser** : Structured Output Parser avec le contenu de `output-parser-soundcloud.json`

### Agent Beatport

1. **Type de node** : AI Agent
2. **MCP Client Configuration** :
   - Transport Type : `SSE`
   - URL : `http://techno-scraper-mcp:8080/sse`
   - Tools : Limiter à `beatport_*`
3. **User Prompt** :
   ```
   Nom du label: {{ $json.name }}
   Date du jour: {{ $json.date }}
   ```
4. **System Prompt** : Copier le contenu de `agent-beatport-system-prompt.md`
5. **Output Parser** : Structured Output Parser avec le contenu de `output-parser-beatport.json`

### Code Node (Merge)

1. **Type de node** : Code
2. **Code** : Copier le contenu de `code-node-merge.js`

## 🔧 Variables requises

- `$json.name` : Nom du label (depuis Google Sheet)
- `$json.date` : Date du jour au format YYYY-MM-DD

## 📤 Format de sortie final

Après le merge, le JSON final contient :

```json
{
  "country": "string",
  "emailDemo": "string",
  "scFollowers": 0,
  "soundcloudLink": "string",
  "facebookLink": "string",
  "instagramLink": "string",
  "beatportLink": "string",
  "bandcampLink": "string",
  "genre": "string",
  "isActive": true,
  "isOpenNew": false
}
```

## 🚀 Déploiement

1. Déployer le serveur MCP sur Dokploy
2. Vérifier que `techno-scraper-mcp` est accessible sur le réseau Docker
3. Créer le workflow n8n selon l'architecture ci-dessus
4. Tester avec un label connu

## 📚 Documentation

Pour plus de détails sur les MCP tools, voir :
- `/docs/mcp-usage.md`
- `/app/mcp/tools/`
