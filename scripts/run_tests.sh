#!/bin/bash

echo "===== Exécution des tests unitaires ====="

# Déterminer si nous sommes dans le répertoire scripts ou à la racine
if [ -f "run_tests.sh" ]; then
    # Nous sommes dans le répertoire scripts
    cd ..
fi

# Activer l'environnement virtuel si nécessaire
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Exécuter tous les tests
echo "Exécution de tous les tests avec couverture..."
pytest -v --cov=app tests/

# Générer un rapport de couverture HTML si demandé
if [ "$1" = "--html" ]; then
    echo "Génération du rapport de couverture HTML..."
    pytest --cov=app --cov-report=html tests/
    echo "Rapport généré dans le dossier htmlcov/"
fi

echo "===== Tests terminés =====" 