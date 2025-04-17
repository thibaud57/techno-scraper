#!/bin/bash

# Script de déploiement pour techno-scraper
# Ce script est utilisé par GitHub Actions pour déployer l'application sur le VPS

set -e  # Arrêter le script en cas d'erreur

# Vérifier que les variables d'environnement nécessaires sont définies
if [ -z "$SSH_HOST" ] || [ -z "$SSH_USERNAME" ] || [ -z "$SSH_PRIVATE_KEY" ]; then
    echo "Erreur: Les variables d'environnement SSH_HOST, SSH_USERNAME et SSH_PRIVATE_KEY doivent être définies"
    exit 1
fi

# Répertoire du projet sur le VPS
PROJECT_DIR="~/techno-scraper"

# Créer le répertoire du projet s'il n'existe pas
ssh -i "$SSH_PRIVATE_KEY" "$SSH_USERNAME@$SSH_HOST" "mkdir -p $PROJECT_DIR"

# Copier les fichiers nécessaires
scp -i "$SSH_PRIVATE_KEY" docker-compose.yml "$SSH_USERNAME@$SSH_HOST:$PROJECT_DIR/"
scp -i "$SSH_PRIVATE_KEY" .env "$SSH_USERNAME@$SSH_HOST:$PROJECT_DIR/"

# Se connecter au VPS et déployer l'application
ssh -i "$SSH_PRIVATE_KEY" "$SSH_USERNAME@$SSH_HOST" << EOF
    cd $PROJECT_DIR
    
    echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin
    
    docker pull ghcr.io/$GITHUB_REPOSITORY:latest
    
    docker-compose down
    
    docker-compose up -d
    
    docker-compose ps
    
    docker image prune -f
EOF

echo "Déploiement terminé avec succès !"