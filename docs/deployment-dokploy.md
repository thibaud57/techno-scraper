# Déploiement sur Dokploy - Techno-Scraper

Guide complet pour déployer techno-scraper (API REST + Serveur MCP) sur Dokploy.

## 📋 Prérequis

- Dokploy installé sur votre VPS
- Compte GitHub connecté à Dokploy
- Repository `thibaud57/techno-scraper` accessible
- Credentials SoundCloud (Client ID + Secret)

## 🎯 Architecture déployée

```
Dokploy
├── Projet: automation (existant)
│   └── Service: n8n
└── Projet: techno-scraper (nouveau)
    ├── Service: techno-scraper-api (REST - legacy)
    └── Service: techno-scraper-mcp (MCP - production)

Réseau partagé: dokploy-network
```

## 🚀 Procédure de déploiement

### Étape 1 : Connecter GitHub à Dokploy

1. Aller dans **Dokploy Panel → Settings → Providers → GitHub**
2. Cliquer sur **Add GitHub Provider**
3. Créer une GitHub App :
   - **Name** : `Dokploy-Techno-Scraper`
   - **Repository Access** : Sélectionner `thibaud57/techno-scraper`
4. Autoriser l'accès
5. La connexion GitHub est maintenant active

### Étape 2 : Créer le projet techno-scraper

1. Dans Dokploy, cliquer sur **New Project**
2. **Project Name** : `techno-scraper`
3. **Description** : "Music platform scraper with REST API + MCP Server"
4. Créer le projet

### Étape 3 : Ajouter le service Docker Compose

1. Dans le projet `techno-scraper`, cliquer sur **Add Service**
2. Sélectionner **Docker Compose**
3. Configuration :

#### Configuration de base
- **Name** : `techno-scraper-stack`
- **Source** : **GitHub**
- **Repository** : `thibaud57/techno-scraper`
- **Branch** : `main` (ou `master`)
- **Compose File Path** : `docker-compose.dokploy.yml`

#### Variables d'environnement

Ajouter les variables suivantes dans l'onglet **Environment** :

```
SOUNDCLOUD_CLIENT_ID=your-soundcloud-client-id
SOUNDCLOUD_CLIENT_SECRET=your-soundcloud-client-secret
API_KEY=your-api-key-for-rest-api
PORT=8000
```

**Important** : Remplacer les valeurs par vos vrais credentials.

#### Réseau

Dans l'onglet **Networks**, s'assurer que `dokploy-network` est bien sélectionné.

### Étape 4 : Activer Auto-Deploy

1. Dans les paramètres du service, aller dans **Git**
2. Activer **Auto Deploy** :
   - ✅ **Enable Auto Deploy**
   - **Branch** : `main`
   - Dokploy créera automatiquement un webhook GitHub

### Étape 5 : Déployer

1. Cliquer sur **Deploy**
2. Dokploy va :
   - Cloner le repository
   - Builder les images Docker (Dockerfile + Dockerfile.mcp)
   - Créer les deux services :
     - `techno-scraper-api` (port 8000 en local)
     - `techno-scraper-mcp` (pas de port, stdio)
   - Connecter au réseau `dokploy-network`

### Étape 6 : Vérifier le déploiement

#### 6.1 Vérifier les conteneurs

```bash
# Sur votre VPS
docker ps | grep techno-scraper

# Vous devriez voir :
# techno-scraper-api      (healthy)
# techno-scraper-mcp      (healthy)
```

#### 6.2 Tester l'API REST

```bash
curl http://localhost:8000/status
# Réponse attendue : {"status":"online","app_name":"techno-scraper","version":"0.1.0"}
```

#### 6.3 Vérifier les logs MCP

```bash
docker logs techno-scraper-mcp
# Vous devriez voir : "MCP server starting..."
```

## 🔗 Configuration n8n pour utiliser le serveur MCP

### Méthode 1 : Exécution Docker dans le réseau

Dans votre projet `automation`, modifier le `docker-compose.yml` de n8n :

```yaml
services:
  n8n:
    # ... votre config existante
    networks:
      - dokploy-network  # Ajouter cette ligne
    volumes:
      - ./n8n-mcp-config.json:/home/node/.n8n/mcp_config.json  # Config MCP

networks:
  dokploy-network:
    external: true
```

### Méthode 2 : Configuration MCP dans n8n

Créer `n8n-mcp-config.json` :

```json
{
  "mcpServers": {
    "techno-scraper": {
      "command": "docker",
      "args": [
        "exec",
        "techno-scraper-mcp",
        "python",
        "-m",
        "app.mcp"
      ]
    }
  }
}
```

### Méthode 3 : Communication directe (si même réseau)

Si n8n supporte MCP nativement et partage le réseau `dokploy-network` :

```json
{
  "mcpServers": {
    "techno-scraper": {
      "command": "python",
      "args": ["-m", "app.mcp"],
      "network": "techno-scraper-mcp"
    }
  }
}
```

## 🧪 Tester la communication MCP

### Depuis n8n

1. Créer un nouveau workflow dans n8n
2. Ajouter un nœud **MCP Tool**
3. Configuration :
   - **Server** : `techno-scraper`
   - **Tool** : `soundcloud_search_profiles`
   - **Arguments** :
     ```json
     {
       "query": "Carl Cox",
       "limit": 10
     }
     ```
4. Exécuter le workflow
5. Vous devriez recevoir une liste de profils SoundCloud

### Depuis le VPS (test manuel)

```bash
# Test du serveur MCP via stdin
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | \
  docker exec -i techno-scraper-mcp python -m app.mcp

# Réponse attendue : Liste des tools disponibles
```

## 🔄 Mises à jour automatiques

Après configuration, chaque push sur la branche `main` déclenchera automatiquement :

1. **Webhook GitHub** → Dokploy
2. **Build** des nouvelles images Docker
3. **Déploiement** automatique
4. **Redémarrage** des services

**Plus besoin de GitHub Actions pour le déploiement !**

## 📊 Monitoring

### Logs en temps réel

Dans le panel Dokploy :
- **Logs API REST** : Onglet Logs du service `techno-scraper-api`
- **Logs MCP** : Onglet Logs du service `techno-scraper-mcp`

### Health checks

Les deux services ont des healthchecks :
- **API REST** : Vérifie `/status` (HTTP)
- **MCP Server** : Vérifie le processus Python

Status visible dans Dokploy Panel.

## 🗑️ Phase 4 : Suppression de l'API REST (après migration complète)

Une fois Beatport et Bandcamp migrés vers MCP :

1. Modifier `docker-compose.dokploy.yml` :
   - Supprimer le service `techno-scraper-api`
   - Garder uniquement `techno-scraper-mcp`

2. Push sur GitHub → Déploiement automatique

3. L'API REST sera supprimée, seul le serveur MCP restera actif

## 🐛 Troubleshooting

### Service MCP ne démarre pas

```bash
# Vérifier les logs
docker logs techno-scraper-mcp

# Erreurs courantes :
# - Variables d'env manquantes (SOUNDCLOUD_CLIENT_ID/SECRET)
# - Module mcp non installé (vérifier requirements.txt)
```

### n8n ne peut pas communiquer avec MCP

```bash
# Vérifier que les deux sont sur le même réseau
docker network inspect dokploy-network

# Vous devriez voir :
# - techno-scraper-mcp
# - n8n (ou votre conteneur n8n)
```

### Healthcheck échoue

```bash
# Tester manuellement
docker exec techno-scraper-mcp pgrep -f "app.mcp"

# Si aucun processus, vérifier les logs
docker logs techno-scraper-mcp
```

## 📚 Ressources

- [Documentation Dokploy](https://docs.dokploy.com/)
- [Docker Compose Networking](https://docs.docker.com/compose/networking/)
- [MCP Usage Guide](./mcp-usage.md)
- [n8n MCP Setup](./n8n-mcp-setup.md)

## 🔐 Sécurité

- Variables d'environnement stockées de manière sécurisée dans Dokploy
- API REST accessible uniquement en local (127.0.0.1)
- Serveur MCP accessible uniquement via réseau Docker interne
- Pas d'exposition publique des services

## ✅ Checklist de déploiement

- [ ] GitHub connecté à Dokploy
- [ ] Projet `techno-scraper` créé
- [ ] Service Docker Compose ajouté
- [ ] Variables d'environnement configurées
- [ ] Auto-deploy activé
- [ ] Premier déploiement réussi
- [ ] Healthchecks verts
- [ ] Logs sans erreur
- [ ] n8n configuré avec MCP
- [ ] Test de communication réussi
- [ ] Webhook GitHub actif

---

**Note** : Ce guide est à jour pour la Phase 1 (SoundCloud MCP). Il sera mis à jour après chaque phase de migration.
