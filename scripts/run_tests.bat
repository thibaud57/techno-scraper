@echo off
echo ===== Exécution des tests unitaires =====

REM Déterminer si nous sommes dans le répertoire scripts ou à la racine
if exist "run_tests.bat" (
    REM Nous sommes dans le répertoire scripts
    cd ..
)

REM Activer l'environnement virtuel si nécessaire
if exist ".venv" (
    call .venv\Scripts\activate
)

REM Exécuter tous les tests
echo Exécution de tous les tests avec couverture...
pytest -v --cov=app tests\

REM Générer un rapport de couverture HTML si demandé
if "%1"=="--html" (
    echo Génération du rapport de couverture HTML...
    pytest --cov=app --cov-report=html tests\
    echo Rapport généré dans le dossier htmlcov\
)

echo ===== Tests terminés =====
pause 