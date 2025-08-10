# Taste Match 🎵🎬📚

**Taste Match est le jeu social qui transforme vos films, musiques et livres préférés en un défi amusant et révélateur avec vos amis. Réglez les débats, découvrez des pépites cachées et trouvez qui est votre véritable âme-sœur culturelle.**

Ce projet vise à créer une application sociale engageante où l'interaction principale est un "défi de goût" ludique et direct entre utilisateurs. L'objectif n'est pas seulement de cataloguer des œuvres culturelles, mais de transformer ces catalogues en un jeu interactif, un véritable "démarreur de conversation".

## 📖 Table des matières

- [🎯 À propos du projet](#à-propos-du-projet)
  - [Proposition de valeur unique](#proposition-de-valeur-unique)
  - [Audience cible](#audience-cible)
- [✨ Fonctionnalités implémentées](#fonctionnalités-implémentées)
- [🛠️ Stack technologique](#stack-technologique)
- [🏗️ Architecture](#architecture)
- [🌐 Déploiement et Environnement de Production](#-déploiement-et-environnement-de-production)

## À propos du projet

Taste Match est né d'un constat simple : les plateformes culturelles existantes comme Letterboxd ou Goodreads sont excellentes pour le catalogage passif, mais manquent d'interaction sociale directe, synchrone et ludique. Taste Match comble cette lacune en ne se contentant pas de permettre la comparaison, mais en la **provoquant** à travers un défi.

Le cœur de l'expérience est le moment de la "révélation" du score de compatibilité, conçu pour susciter une réaction émotionnelle et lancer une conversation : la surprise, la validation ou le débat amical.

### Proposition de valeur unique

Taste Match se différencie du paysage concurrentiel sur plusieurs points clés :

- **Actif vs. Passif :** L'application crée des défis interactifs plutôt que de simplement afficher des listes.
- **Ludique vs. Archivage :** C'est un jeu, pas une simple base de données. L'objectif est le "match".
- **Révélation Synchrone vs. Navigation Asynchrone :** La magie réside dans la découverte simultanée et partagée des résultats.

### Audience cible

La conception s'adresse à plusieurs types d'utilisateurs :

1. **Le Couple Décontracté (Alex & Ben) :** Cherche des moyens amusants de se connecter et de décider quoi regarder ou écouter.
2. **La Cinéphile Passionnée (Chloé) :** Utilise l'application pour démontrer son expertise et défier les membres de son ciné-club avec des listes pointues.
3. **L'Organisatrice Sociale (Maria) :** Gère des clubs (lecture, jeux) et utilise l'application pour engager sa communauté et prendre des décisions de groupe.

## Fonctionnalités implémentées

### 🎯 Fonctionnalités Core

- **Système d'authentification JWT** : Inscription et connexion sécurisées
- **Gestion des listes culturelles** : Création automatique de listes par catégorie (Films, Séries, Musique, Livres)
- **Recherche et ajout externe** : Intégration avec TMDB (films/séries), Spotify (musique) et Google Books (livres)
- **Interface utilisateur moderne** : Design responsive avec Material-UI et Tailwind CSS

### 📱 Pages et Navigation

- **Page Accueil** : Vue d'ensemble des activités récentes
- **Page Découvrir** : Exploration de contenus tendance avec suggestions personnalisées
- **Page Match** : Interface de comparaison de goûts (en développement)
- **Page Listes** : Gestion complète des collections personnelles avec affichage par catégorie
- **Page Profil** : Gestion du compte utilisateur

### 🔍 Recherche et Découverte

- **Barre de recherche intelligente** : Recherche en temps réel dans les APIs externes
- **Contenu tendance** : Suggestions populaires depuis TMDB, Spotify et Google Books
- **Ajout rapide** : Import direct depuis les résultats de recherche vers les listes
- **Métadonnées enrichies** : Images, descriptions, notes et informations détaillées

### 🎨 Expérience Utilisateur

- **Design glassmorphism** : Interface moderne avec effets de transparence
- **Navigation fluide** : Navigation bottom pour mobile avec transitions animées
- **Feedback visuel** : Animations et états de chargement pour une expérience optimale
- **Gestion d'erreurs** : Messages d'erreur contextuels et fallbacks gracieux

### 🔮 Fonctionnalités à venir

- **Mécanique de "Match" gamifiée** : Algorithme de compatibilité avec scoring
- **Défis de groupe** : Comparaisons multi-utilisateurs
- **Écran de résultats viral** : Partage de résultats avec visualisations
- **Listes collaboratives** : Création de listes à plusieurs
- **Système de badges et succès** : Gamification de l'engagement

### 🧩 Endpoint Match Action (B2)

Un nouvel endpoint permet maintenant d'enregistrer les actions utilisateur sur les recommandations afin d'alimenter les préférences et futures mécaniques de compatibilité.

| Méthode | URL                  | Auth | Description                                                              |
| ------- | -------------------- | ---- | ------------------------------------------------------------------------ |
| POST    | `/api/match/action/` | JWT  | Enregistre / met à jour une action utilisateur sur un contenu recommandé |

#### Payload accepté (alias front inclus)

```json
{
  "external_id": "fb_movie_001",
  "source": "tmdb",
  "category": "FILMS", // alias accepté pour content_type
  // ou "content_type": "FILMS",
  "action": "like", // alias normalisé -> liked
  // valeurs acceptées (alias -> interne): like→liked, dislike→disliked, add→added, skip→skipped
  "title": "Inception",
  "metadata": { "popularity": 80 },
  "description": "Thriller SF" // optionnel (fusionné avec metadata.description)
}
```

#### Réponse (201)

```json
{
  "success": true,
  "action": "liked",
  "preference_id": 123,
  "updated": false, // true si changement d'action (ex: liked -> added)
  "list_id": 5, // présents uniquement si action == added et création list item
  "list_item_id": 42
}
```

#### Règles clés

- Idempotent: répéter la même action ne crée pas de doublon (même preference_id, `updated=false`).
- Changer d'action (ex: like -> add) met à jour la préférence (`updated=true`).
- `added` déclenche la création (ou réutilisation) d'une liste catégorie + insertion item + référence externe.
- Validation stricte: action inconnue => HTTP 400.

Voir aussi `docs/match_action_endpoint.md` pour plus de détails.

## Stack technologique

La stack est choisie pour une architecture découplée, moderne et scalable, prête pour une application web interactive.

| Composant              | Technologie                        | Justification                                                                                                       |
| :--------------------- | :--------------------------------- | :------------------------------------------------------------------------------------------------------------------ |
| **Framework Backend**  | **Django + Django REST Framework** | Fournit une API REST robuste et sécurisée. DRF est le standard pour construire des API avec Django.                 |
| **Framework Frontend** | **React**                          | Crée une interface utilisateur riche, rapide et moderne (Single-Page Application), totalement découplée du backend. |
| **Base de Données**    | **PostgreSQL**                     | Indispensable pour une application sociale, gère une forte concurrence et assure la parité dev/prod.                |
| **Mise en Cache**      | **Redis**                          | Essentiel pour améliorer les performances et respecter les limites de débit des APIs externes.                      |
| **File de Tâches**     | **Celery**                         | Permet d'exécuter des tâches longues en arrière-plan pour une expérience utilisateur fluide.                        |
| **Déploiement**        | **Docker + Nginx**                 | Docker conteneurise l'environnement. Nginx sert le frontend React et agit comme reverse proxy pour l'API.           |

### 🔗 APIs Externes Intégrées

| Service              | Utilisation           | Fonctionnalités                              |
| :------------------- | :-------------------- | :------------------------------------------- |
| **TMDB API**         | Films et séries       | Recherche, métadonnées, images, tendances    |
| **Spotify Web API**  | Musique et albums     | Recherche d'albums, métadonnées artistiques  |
| **Google Books API** | Livres et littérature | Recherche, couvertures, informations éditeur |

### 🚀 État Technique Actuel

- ✅ **Backend API** : Endpoints REST complets pour authentification, listes, recherche
- ✅ **Frontend React** : Interface utilisateur responsive avec navigation SPA
- ✅ **Intégrations externes** : TMDB, Spotify, Google Books fonctionnels
- ✅ **Base de données** : Modèles Django pour utilisateurs, listes et références externes
- ✅ **Cache et optimisations** : Redis pour mise en cache des APIs externes
- ✅ **Authentification** : JWT avec refresh tokens
- 🔄 **Tests** : Tests unitaires backend partiels
- ⏳ **Déploiement prod** : Configuration Docker prête

## Architecture

L'architecture est découplée (headless), avec un frontend React et un backend Django qui communiquent via une API REST.

```bash
┌─────────────────┐    HTTP/JSON     ┌──────────────────┐
│   Frontend      │ ◄──────────────► │   Backend API    │
│   (React)       │                  │   (Django DRF)   │
│   Port 3000     │                  │   Port 8000      │
└─────────────────┘                  └──────────────────┘
                                              │
                                              ▼
                                     ┌──────────────────┐
                                     │   PostgreSQL     │
                                     │   Database       │
                                     └──────────────────┘
                                              │
                                              ▼
                                     ┌──────────────────┐
                                     │   Redis Cache    │
                                     │   (API Cache)    │
                                     └──────────────────┘
```

## 🌐 Déploiement et Environnement de Production

L'application est déployée sur **Render**, une plateforme cloud moderne qui simplifie la gestion d'applications conteneurisées.

### Services sur Render

Le projet est divisé en trois services principaux sur Render :

1. **Frontend (Web Service)** : Sert l'application React. C'est le service exposé publiquement.
2. **Backend (Web Service)** : Fait tourner l'API Django. Il communique avec le frontend et la base de données.
3. **Database (PostgreSQL)** : La base de données managée par Render. Elle n'est accessible que par le service backend via le réseau privé de Render.

### Configuration d'un Domaine Personnalisé

Pour rendre l'application accessible via un nom de domaine personnalisé (ex: `t4st3m4tch.ybdn.fr`), voici les étapes clés :

1. **Côté Render (Service Frontend)** :

   - Dans les paramètres du service frontend, allez dans la section **"Custom Domains"**.
   - Ajoutez votre nom de domaine complet (ex: `t4st3m4tch.ybdn.fr`).
   - Render vous fournira une URL cible se terminant par `.onrender.com`.

2. **Côté Fournisseur DNS (ex: OVH, Gandi, GoDaddy)** :

   - Accédez à la gestion de la zone DNS de votre nom de domaine.
   - Créez un nouvel enregistrement de type **`CNAME`**.
   - Configurez cet enregistrement pour faire pointer votre sous-domaine (ex: `t4st3m4tch`) vers l'URL cible fournie par Render à l'étape précédente.

3. **Côté Render (Service Backend) - Crucial pour CORS** :
   - Le frontend (servi depuis votre nouveau domaine) et le backend (servi depuis une URL `.onrender.com`) n'ont pas la même "origine". Pour autoriser la communication entre eux, il est impératif de mettre à jour la configuration CORS du backend.
   - Dans les paramètres du service backend sur Render, allez dans la section **"Environment"**.
   - Ajoutez ou modifiez la variable d'environnement `CORS_ALLOWED_ORIGINS`.
   - Assurez-vous que cette variable contienne l'URL de votre frontend, préfixée par `https://` (ex: `https://t4st3m4tch.ybdn.fr`). Si plusieurs domaines sont nécessaires, séparez-les par une virgule.
   - Exemple de valeur : `https://tastematch-app.onrender.com,https://t4st3m4tch.ybdn.fr`

Après avoir sauvegardé les variables d'environnement, Render redéploiera automatiquement le service backend avec la nouvelle configuration, résolvant ainsi les erreurs CORS.

## 🏁 Démarrage rapide

### Prérequis

- **Docker & Docker Compose** : Pour l'environnement de développement
- **Node.js 18+** : Pour le développement frontend
- **Python 3.11+** : Pour le développement backend
- **Git** : Pour la gestion de version

### 1. Clonage et configuration

```bash
# Cloner le repository
git clone https://github.com/ybdn/T4ST3_M4TCH.git
cd T4ST3_M4TCH

# Copier les fichiers d'environnement
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env  # si nécessaire
```

### 2. Configuration des APIs externes (optionnel)

Pour un fonctionnement optimal, configurez les clés API dans `backend/.env` :

```env
# TMDB (The Movie Database) - Films & Séries
TMDB_API_KEY=your_tmdb_api_key

# Spotify Web API - Musique
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# Google Books API - Livres
GOOGLE_BOOKS_API_KEY=your_google_books_api_key
```

> **Note** : L'application fonctionne sans ces clés mais avec des fonctionnalités limitées.

### 3. Lancement avec Docker

```bash
# Lancer tous les services
docker-compose up

# En arrière-plan
docker-compose up -d
```

**Services démarrés :**

- **Frontend React** : <http://localhost:3000>
- **Backend API** : <http://localhost:8000>
- **PostgreSQL** : localhost:5432
- **Redis** : localhost:6379

### 4. Configuration initiale

```bash
# Créer les migrations
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# Créer un superutilisateur (optionnel)
docker-compose exec backend python manage.py createsuperuser
```

### 5. Accès à l'application

1. **Frontend** : Ouvrir <http://localhost:3000>
2. **S'inscrire** ou se connecter
3. **Explorer** les fonctionnalités :
   - Page Découvrir pour voir les tendances
   - Page Listes pour gérer vos collections
   - Barre de recherche pour ajouter du contenu

### Développement

```bash
# Frontend (développement avec hot reload)
cd frontend
npm install
npm run dev

# Backend (développement)
cd backend
python manage.py runserver 0.0.0.0:8000

# Tests backend
python manage.py test

# Logs en temps réel
docker-compose logs -f
```
