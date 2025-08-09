# Configuration de Développement T4ST3_M4TCH

## 🚀 Démarrage Rapide

### Prérequis

- Docker et Docker Compose installés
- Git configuré

### Lancement de l'environnement de développement

```bash
# Option 1: Script automatique (recommandé)
./scripts/dev-start.sh

# Option 2: Manuel
docker-compose -f docker-compose.local.yml up --build
```

### Accès aux services

- **Frontend**: <http://localhost:3000>
- **Backend API**: <http://localhost:8000>
- **Admin Django**: <http://localhost:8000/admin/>
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Arrêt de l'environnement

```bash
# Option 1: Script
./scripts/dev-stop.sh

# Option 2: Manuel
docker-compose -f docker-compose.local.yml down
```

## 🏗️ Architecture Dev vs Prod

### Développement Local

- **Fichiers**: `docker-compose.local.yml`, `backend/.env.local`, `frontend/.env.local`
- **Base de données**: PostgreSQL locale (Docker)
- **Hot reload**: Activé pour backend et frontend
- **CORS**: Permissif (localhost:3000)
- **Debug**: Activé

### Production (Render)

- **Fichiers**: `render.yaml`, variables d'environnement Render
- **Base de données**: PostgreSQL managée (Render)
- **Déploiement**: Automatique via push sur `main`
- **CORS**: Restrictif (domaine spécifique)
- **Debug**: Désactivé

## 🔧 Configuration

### Variables d'Environnement

**backend/.env.local** (développement):

```bash
SECRET_KEY=django-insecure-dev-key-for-local-development-only
DEBUG=True
DATABASE_URL=postgresql://tastematch:tastematch@db:5432/tastematch
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Clés API - remplacer par les vraies valeurs
TMDB_API_KEY=ta_cle_tmdb
SPOTIFY_CLIENT_ID=ton_client_id_spotify
SPOTIFY_CLIENT_SECRET=ton_secret_spotify
GOOGLE_BOOKS_API_KEY=ta_cle_google_books
```

**frontend/.env.local** (développement):

```bash
VITE_API_URL=http://localhost:8000
```

## 📝 Workflow de Développement

### 1. Développement Local

```bash
# Basculer sur la branche de développement
git checkout dev

# Démarrer l'env de dev
./scripts/dev-start.sh

# Faire tes modifications...

# Les changements sont automatiquement rechargés
# Backend: Django reloader
# Frontend: Vite HMR
```

### 2. Tests et Validation

```bash
# Tests backend
docker-compose -f docker-compose.local.yml exec backend python manage.py test

# Linting frontend (si configuré)
cd frontend && npm run lint
```

### 3. Déploiement

```bash
# Commit sur dev
git add .
git commit -m "feat: nouvelle fonctionnalité"
git push origin dev

# Quand prêt pour production
git checkout main
git merge dev
git push origin main  # Déclenche le déploiement Render
```

## 🛠️ Commandes Utiles

### Backend (Django)

```bash
# Shell Django
docker-compose -f docker-compose.local.yml exec backend python manage.py shell

# Créer migrations
docker-compose -f docker-compose.local.yml exec backend python manage.py makemigrations

# Appliquer migrations
docker-compose -f docker-compose.local.yml exec backend python manage.py migrate

# Créer superuser
docker-compose -f docker-compose.local.yml exec backend python manage.py createsuperuser
```

### Frontend (React/Vite)

```bash
# Installer dépendances
cd frontend && npm install

# Build de production
cd frontend && npm run build

# Développement local (hors Docker)
cd frontend && npm run dev
```

### Base de données

```bash
# Se connecter à PostgreSQL
docker-compose -f docker-compose.local.yml exec db psql -U tastematch -d tastematch

# Backup
docker-compose -f docker-compose.local.yml exec db pg_dump -U tastematch tastematch > backup.sql
```

## 🔍 Troubleshooting

### Problème: "Container unhealthy"

- **Cause**: Le healthcheck du backend est trop strict
- **Solution**: Attendre ~1 minute ou redémarrer les services

### Problème: "Database connection refused"

- **Cause**: Le backend démarre avant PostgreSQL
- **Solution**: Les healthchecks devraient résoudre automatiquement

### Problème: Frontend n'accède pas au backend

- **Cause**: Variables d'environnement CORS ou VITE_API_URL incorrectes
- **Solution**: Vérifier `backend/.env.local` et `frontend/.env.local`

### Problème: Hot reload ne fonctionne pas

- **Cause**: Volumes Docker mal configurés
- **Solution**: Redémarrer avec `docker-compose down -v` puis relancer

## 📁 Structure des Fichiers

```bash
T4ST3_M4TCH/
├── docker-compose.yml          # Production (Render)
├── docker-compose.local.yml    # Développement local
├── render.yaml                 # Config déploiement Render
├── scripts/
│   ├── dev-start.sh           # Script de démarrage dev
│   └── dev-stop.sh            # Script d'arrêt dev
├── backend/
│   ├── .env                   # Production (placeholders)
│   ├── .env.local             # Développement (vraies clés)
│   └── ...
├── frontend/
│   ├── .env.local             # Config dev frontend
│   └── ...
└── .gitignore                 # Ignore .env.local
```

## ⚠️ Sécurité

- **JAMAIS** commit `backend/.env.local` (contient les vraies clés API)
- Les clés de production sont gérées dans le dashboard Render
- Le fichier `backend/.env` ne contient que des placeholders
