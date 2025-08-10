# Guide de Contribution - T4ST3_M4TCH 🎵🎬📚

Merci de votre intérêt pour contribuer à T4ST3_M4TCH ! Ce guide vous aidera à commencer et à suivre nos meilleures pratiques de développement.

## 📋 Table des matières

- [🚀 Démarrage rapide](#-démarrage-rapide)
- [🏗️ Configuration de l'environnement](#️-configuration-de-lenvironnement)
- [🔄 Workflow de développement](#-workflow-de-développement)
- [📝 Conventions de commit](#-conventions-de-commit)
- [🧪 Tests](#-tests)
- [🎨 Style de code](#-style-de-code)
- [📖 Pull Requests](#-pull-requests)
- [🔧 Dépannage](#-dépannage)
- [📞 Support](#-support)

## 🚀 Démarrage rapide

### Prérequis

- **Docker & Docker Compose** (version récente)
- **Git** configuré avec votre nom et email
- **Node.js 18+** (pour le développement frontend local)
- **Python 3.11+** (pour le développement backend local)

### Installation rapide

```bash
# 1. Cloner le repository
git clone https://github.com/ybdn/T4ST3_M4TCH.git
cd T4ST3_M4TCH

# 2. Copier les fichiers de configuration
cp backend/.env.example backend/.env.local
cp frontend/.env.example frontend/.env.local

# 3. Démarrer l'environnement de développement
./scripts/dev-start.sh
```

**Accès aux services :**
- Frontend : http://localhost:3000
- Backend API : http://localhost:8000
- Admin Django : http://localhost:8000/admin/

> 📖 Pour plus de détails sur la configuration, consultez [DEV_SETUP.md](./DEV_SETUP.md)

## 🏗️ Configuration de l'environnement

### Variables d'environnement

**backend/.env.local** (développement) :
```bash
SECRET_KEY=django-insecure-dev-key-change-me-in-production
DEBUG=True
DATABASE_URL=postgresql://tastematch:tastematch@db:5432/tastematch
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# APIs externes (optionnel pour débuter)
TMDB_API_KEY=your_tmdb_api_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
GOOGLE_BOOKS_API_KEY=your_google_books_api_key
```

**frontend/.env.local** :
```bash
VITE_API_URL=http://localhost:8000
```

### Configuration initiale de la base de données

```bash
# Créer et appliquer les migrations
docker compose -f docker-compose.local.yml exec backend python manage.py makemigrations
docker compose -f docker-compose.local.yml exec backend python manage.py migrate

# Créer un superutilisateur (optionnel)
docker compose -f docker-compose.local.yml exec backend python manage.py createsuperuser
```

## 🔄 Workflow de développement

### 1. Nouvelle fonctionnalité ou correction

```bash
# Créer une nouvelle branche depuis dev
git checkout dev
git pull origin dev
git checkout -b feature/ma-nouvelle-fonctionnalite

# Ou pour une correction de bug
git checkout -b fix/correction-bug-specifique
```

### 2. Développement

```bash
# Démarrer l'environnement de développement
./scripts/dev-start.sh

# Vos modifications sont automatiquement rechargées :
# - Backend : Django auto-reload
# - Frontend : Vite HMR (Hot Module Replacement)
```

### 3. Tests et validation

```bash
# Tests backend
docker compose -f docker-compose.local.yml exec backend python manage.py test

# Linting frontend
cd frontend && npm run lint

# Build frontend pour vérifier qu'il n'y a pas d'erreurs
cd frontend && npm run build
```

### 4. Commit et push

```bash
# Suivre les conventions de commit (voir section suivante)
git add .
git commit -m "feat: ajouter recherche de films via TMDB API"
git push origin feature/ma-nouvelle-fonctionnalite
```

### 5. Pull Request

- Créer une PR vers la branche `dev`
- Remplir le template de PR avec une description claire
- Assigner des reviewers si nécessaire
- Répondre aux commentaires de review

## 📝 Conventions de commit

Nous utilisons la convention **Conventional Commits** pour maintenir un historique clair et permettre la génération automatique de changelogs.

### Format

```
<type>(<scope>): <description>

<body optionnel>

<footer optionnel>
```

### Types principaux

| Type | Description | Exemple |
|------|-------------|---------|
| `feat` | Nouvelle fonctionnalité | `feat: ajouter système de match de goûts` |
| `fix` | Correction de bug | `fix: résoudre erreur 500 lors de la recherche` |
| `docs` | Documentation | `docs: mettre à jour le README` |
| `style` | Formatage, points-virgules manquants, etc. | `style: corriger indentation composant Header` |
| `refactor` | Refactoring sans changement de fonctionnalité | `refactor: simplifier service de recherche` |
| `test` | Ajout ou modification de tests | `test: ajouter tests pour API de listes` |
| `chore` | Tâches de maintenance | `chore: mettre à jour dépendances` |

### Scopes suggérés

- `api` : Backend Django/DRF
- `ui` : Interface utilisateur React
- `auth` : Authentification
- `db` : Base de données / migrations
- `search` : Fonctionnalités de recherche
- `lists` : Gestion des listes
- `match` : Système de matching
- `docker` : Configuration Docker
- `ci` : Intégration continue

### Exemples

```bash
# Nouvelle fonctionnalité
feat(api): ajouter endpoint pour partage de listes
feat(ui): implémenter page de résultats de match

# Correction de bug
fix(auth): corriger validation des tokens JWT
fix(search): gérer les erreurs d'API externe

# Documentation
docs: ajouter guide de contribution
docs(api): documenter endpoints de l'API

# Refactoring
refactor(ui): restructurer composants de navigation
refactor(api): optimiser requêtes de base de données
```

## 🧪 Tests

### Backend (Django)

```bash
# Exécuter tous les tests
docker compose -f docker-compose.local.yml exec backend python manage.py test

# Tests spécifiques à une app
docker compose -f docker-compose.local.yml exec backend python manage.py test core

# Tests avec couverture (si configuré)
docker compose -f docker-compose.local.yml exec backend coverage run --source='.' manage.py test
docker compose -f docker-compose.local.yml exec backend coverage report
```

**Conventions pour les tests backend :**
- Un fichier `tests.py` par app Django
- Classes de test héritant de `TestCase` ou `APITestCase`
- Méthodes de test commençant par `test_`
- Utiliser des factories pour les données de test
- Mocker les appels aux APIs externes

Exemple :
```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

class ListAPITestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_list(self):
        data = {'name': 'Ma liste de films', 'category': 'movies'}
        response = self.client.post('/api/lists/', data)
        self.assertEqual(response.status_code, 201)
```

### Frontend (React)

```bash
# Linting
cd frontend && npm run lint

# Build pour détecter les erreurs TypeScript
cd frontend && npm run build

# Tests unitaires (à configurer)
# cd frontend && npm run test
```

**Conventions pour le frontend :**
- Utiliser ESLint pour le formatage et les bonnes pratiques
- Suivre les règles TypeScript strictes
- Composants en PascalCase
- Hooks personnalisés préfixés par `use`
- Pas de `console.log` en production

## 🎨 Style de code

### Backend (Python/Django)

- Suivre **PEP 8** pour le style Python
- Noms de variables/fonctions en `snake_case`
- Classes en `PascalCase`
- Constantes en `UPPER_CASE`
- Docstrings pour les fonctions complexes
- Imports organisés : stdlib, third-party, local

```python
# Bon exemple
from typing import Optional
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import List

User = get_user_model()

class ListSerializer(serializers.ModelSerializer):
    """Serializer pour les listes utilisateur."""
    
    owner = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = List
        fields = ['id', 'name', 'category', 'owner', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at']
```

### Frontend (TypeScript/React)

- Utiliser **ESLint** avec la configuration du projet
- Composants fonctionnels avec hooks
- Props typées avec TypeScript
- Noms de fichiers en `kebab-case`
- Composants en `PascalCase`

```typescript
// Bon exemple
interface MovieCardProps {
  movie: {
    id: number;
    title: string;
    posterUrl?: string;
  };
  onAdd: (movieId: number) => void;
}

export const MovieCard: React.FC<MovieCardProps> = ({ movie, onAdd }) => {
  const handleAddClick = () => {
    onAdd(movie.id);
  };

  return (
    <div className="movie-card">
      <h3>{movie.title}</h3>
      <button onClick={handleAddClick}>Ajouter</button>
    </div>
  );
};
```

## 📖 Pull Requests

### Avant de créer une PR

- [ ] Tests passent en local
- [ ] Code respecte les conventions de style
- [ ] Documentation mise à jour si nécessaire
- [ ] Pas de `console.log` ou `print()` de debug
- [ ] Variables d'environnement sensibles non commitées

### Template de PR

```markdown
## 📝 Description

Brève description des changements apportés.

## 🔗 Issue liée

Fixe #(numéro de l'issue)

## 🧪 Tests

- [ ] Tests existants passent
- [ ] Nouveaux tests ajoutés si nécessaire
- [ ] Testé manuellement dans le navigateur

## 📸 Screenshots (si applicable)

Ajouter des captures d'écran pour les changements d'UI.

## ✅ Checklist

- [ ] Code respecte les conventions de style
- [ ] Documentation mise à jour
- [ ] Pas de code de debug
- [ ] Variables sensibles non exposées
```

### Process de review

1. **Auto-review** : Relire sa propre PR avant de la soumettre
2. **Tests automatiques** : S'assurer que les workflows GitHub passent
3. **Review par les pairs** : Attendre l'approbation d'au moins un reviewer
4. **Merge** : Squash and merge vers `dev`, puis merge `dev` vers `main` pour le déploiement

## 🔧 Dépannage

### Problèmes courants

#### "Container unhealthy"
```bash
# Attendre ~1 minute ou redémarrer
docker compose -f docker-compose.local.yml down
docker compose -f docker-compose.local.yml up
```

#### "Database connection refused"
```bash
# Vérifier que PostgreSQL est bien démarré
docker compose -f docker-compose.local.yml logs db
```

#### Frontend n'accède pas au backend
```bash
# Vérifier les variables d'environnement
cat frontend/.env.local
# Doit contenir : VITE_API_URL=http://localhost:8000
```

#### Erreurs CORS
```bash
# Vérifier la configuration backend
cat backend/.env.local
# Doit contenir : CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Commandes utiles

```bash
# Redémarrer complètement l'environnement
docker compose -f docker-compose.local.yml down -v
docker compose -f docker-compose.local.yml up --build

# Voir les logs en temps réel
docker compose -f docker-compose.local.yml logs -f

# Accéder au shell Django
docker compose -f docker-compose.local.yml exec backend python manage.py shell

# Accéder à la base de données
docker compose -f docker-compose.local.yml exec db psql -U tastematch -d tastematch
```

## 📞 Support

### Ressources

- **Documentation technique** : [DEV_SETUP.md](./DEV_SETUP.md)
- **Architecture** : Voir README.md section Architecture
- **APIs externes** : TMDB, Spotify, Google Books

### Obtenir de l'aide

1. **Issues GitHub** : Pour les bugs et demandes de fonctionnalités
2. **Discussions** : Pour les questions générales
3. **Review de code** : Utiliser `@claude` dans les commentaires pour une review IA

### Contribuer à la documentation

- **Typos/corrections** : PR directe
- **Nouveaux guides** : Créer une issue pour discussion
- **Exemples de code** : Toujours les plus récents et testés

---

**Merci de contribuer à T4ST3_M4TCH ! 🎉**

Votre participation aide à créer une meilleure expérience pour découvrir et partager les goûts culturels.