# GitHub Actions Workflows

## 📋 État des workflows après migration Dokploy

### ✅ Workflows actifs

#### `test.yml` - Tests automatiques
- **Déclenché sur** : Pull requests vers `master`
- **Objectif** : Valider le code avant merge (tests unitaires + intégration)
- **À conserver** : Oui, utile pour validation pre-merge

#### `manual-test.yml` - Tests manuels
- **Déclenché sur** : Manuel uniquement
- **Objectif** : Lancer les tests à la demande
- **À conserver** : Oui, utile pour debugging

### ❌ Workflows obsolètes (après migration Dokploy)

#### `deploy.yml` - Déploiement VPS (OBSOLÈTE)
- **Remplacé par** : Auto-deploy Dokploy via webhook GitHub
- **Statut** : À supprimer après confirmation Dokploy
- **Raison** : Dokploy gère le déploiement automatiquement

#### `build.yml` - Build image Docker (OBSOLÈTE)
- **Remplacé par** : Build local Dokploy
- **Statut** : À supprimer après confirmation Dokploy
- **Raison** : Dokploy build les images sur le VPS directement

## 🔄 Migration CI/CD

### Avant (GitHub Actions)
```
Push sur master
  → test.yml (tests)
  → build.yml (build image + push GitHub Registry)
  → deploy.yml (SSH VPS + docker-compose pull + restart)
```

### Après (Dokploy)
```
Push sur master
  → test.yml (tests - validation pre-merge)
  → Webhook GitHub → Dokploy
  → Dokploy (clone + build + deploy automatique)
```

## 📝 Plan de nettoyage

### Phase 1 : Validation Dokploy
- [ ] Déployer sur Dokploy
- [ ] Tester le déploiement automatique (push sur `main`)
- [ ] Vérifier que les deux services fonctionnent (REST + MCP)
- [ ] Tester la communication n8n ↔ MCP

### Phase 2 : Nettoyage workflows
- [ ] Supprimer `.github/workflows/deploy.yml`
- [ ] Supprimer `.github/workflows/build.yml`
- [ ] Mettre à jour ce README
- [ ] Simplifier `test.yml` si nécessaire

### Phase 3 : Nettoyage secrets GitHub
- [ ] Supprimer les secrets inutilisés :
  - `VPS_HOST`
  - `VPS_USER`
  - `VPS_SSH_KEY`
  - `GHCR_TOKEN` (si inutilisé ailleurs)
- [ ] Garder uniquement les secrets pour tests

## 🛠️ Workflows à conserver long terme

```yaml
# test.yml - Toujours utile
name: Tests
on:
  pull_request:
  push:
    branches: [main, master]
```

## 📚 Documentation

- [Dokploy Deployment Guide](../../DOKPLOY_DEPLOYMENT.md)
- [MCP Usage](../../MCP_USAGE.md)
- [Architecture](../../docs/architecture.md)
