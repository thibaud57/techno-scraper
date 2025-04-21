#!/bin/bash

# Script de déploiement pour techno-scraper
# Ce script est utilisé par GitHub Actions pour déployer l'application sur le VPS

set -e  # Arrêter le script en cas d'erreur

# Vérifier que les variables d'environnement nécessaires sont définies
if [ -z "$GITHUB_TOKEN" ] || [ -z "$GITHUB_ACTOR" ] || [ -z "$GITHUB_REPOSITORY" ]; then
    echo "Erreur: Les variables d'environnement GITHUB_TOKEN, GITHUB_ACTOR et GITHUB_REPOSITORY doivent être définies"
    exit 1
fi

echo "Création du réseau 'my_network' si nécessaire..."
docker network create my_network 2>/dev/null || echo "Le réseau 'my_network' existe déjà."

echo "Début du déploiement..."

# Se connecter à GitHub Container Registry
echo "Connexion à GitHub Container Registry..."
echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin

# Télécharger la dernière image
echo "Téléchargement de la dernière image..."
docker pull ghcr.io/$GITHUB_REPOSITORY:latest

# Arrêter les containers existants
echo "Arrêt des containers existants..."
docker compose down

# Démarrer les nouveaux containers
echo "Démarrage des nouveaux containers..."
docker compose up -d

# Afficher l'état des containers
echo "État des containers:"
docker compose ps

# Nettoyer les anciennes images
echo "Nettoyage des anciennes images..."
docker image prune -f

echo "Déploiement terminé avec succès !"