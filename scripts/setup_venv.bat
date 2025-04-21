@echo off
echo ===== Configuration de l'environnement virtuel Python =====

REM Déterminer si nous sommes dans le répertoire scripts ou à la racine
if exist "setup_venv.bat" (
    REM Nous sommes dans le répertoire scripts
    cd ..
)

echo Création de l'environnement virtuel...
python -m venv .venv

echo Activation de l'environnement virtuel...
call .venv\Scripts\activate

echo Installation des dépendances de l'application...
pip install -r requirements.txt

echo Installation des dépendances de test...
pip install -r requirements-test.txt

echo ===== Configuration terminée =====
echo Pour activer cet environnement à l'avenir, exécutez: .venv\Scripts\activate
echo Pour démarrer le serveur de développement, exécutez: scripts\run_dev_server.bat
echo Pour exécuter les tests unitaires, exécutez: pytest -v --cov=app tests
pause