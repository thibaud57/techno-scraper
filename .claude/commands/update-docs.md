# Mise à jour de la documentation

Cette commande demande à Claude de mettre à jour l'ensemble de la documentation du projet techno-scraper.

## Documentation à mettre à jour

### 1. README.md (racine du projet)
- Vue d'ensemble du projet
- Instructions d'installation et configuration
- Utilisation de l'API
- Exemples d'endpoints

### 2. tests/README.md
- Structure et organisation des tests
- Instructions pour exécuter les tests
- Patterns de test utilisés

### 3. docs/architecture.md  
- Architecture générale du projet
- Diagrammes et flux de données
- Composants principaux
- Structure des dossiers

### 4. docs/DEVELOPMENT.md
- **IMPORTANT: Ajouter la date du jour au format (DD/MM/YYYY)**
- Ajouter les nouvelles fonctionnalités implémentées depuis la dernière mise à jour
- État actuel du projet
- Modifications récentes avec contexte technique
- Prochaines étapes

## Instructions pour Claude

1. **Détecter les changements récents** (3 méthodes) :
   **Option 1 - Changements non-committés :**
   - Examiner `git status` pour voir les fichiers modifiés/ajoutés
   - Lire les nouveaux fichiers créés depuis la dernière date
   **Option 2 - Changements committés :**
   - Lire `git log --oneline -10` pour les derniers commits
   - Analyser `git diff HEAD~5..HEAD --name-only` pour les fichiers récents
   **Option 3 - Manuel :**
   - Demander à l'utilisateur de préciser les changements via argument
   **Dans tous les cas :** Comparer avec la dernière date dans `docs/DEVELOPMENT.md`

2. **Identifier automatiquement les nouveautés** :
   - Nouveaux fichiers dans `app/`, `tests/`
   - Modifications dans les scrapers/routers/services
   - Nouveaux tests créés
   - Changements d'architecture

3. **Mettre à jour DEVELOPMENT.md** :
   - Ajouter nouvelle section avec **date du jour (DD/MM/YYYY)**
   - Lister les features/améliorations détectées
   - Conserver le style technique existant

4. **Réviser les autres docs** pour cohérence

5. **Rester concis** - juste l'essentiel

## Style à respecter

- **Concis et technique** pour DEVELOPMENT.md
- **Pratique et utile** pour les README
- **Détaillé mais organisé** pour architecture.md
- **Utiliser les dates** au format français (DD/MM/YYYY)
- **Sections chronologiques** dans DEVELOPMENT.md (plus récent en haut)