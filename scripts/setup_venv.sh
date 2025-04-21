#!/bin/bash

echo "===== Configuration de l'environnement virtuel Python ====="

# Déterminer si nous sommes dans le répertoire scripts ou à la racine
if [ -f "setup_venv.sh" ]; then
    # Nous sommes dans le répertoire scripts
    cd ..
fi

echo "Création de l'environnement virtuel..."
python3 -m venv .venv

echo "Activation de l'environnement virtuel..."
source .venv/bin/activate

echo "Installation des dépendances de l'application..."
pip install -r requirements.txt

echo "Installation des dépendances de test..."
pip install -r requirements-test.txt

echo "===== Configuration terminée ====="
echo "Pour activer cet environnement à l'avenir, exécutez: source .venv/bin/activate"
echo "Pour démarrer le serveur de développement, exécutez: ./scripts/run_dev_server.sh"
echo "Pour exécuter les tests unitaires, exécutez: pytest -v --cov=app tests"
echo

# Attendre que l'utilisateur appuie sur une touche
read -p "Appuyez sur Entrée pour continuer..."