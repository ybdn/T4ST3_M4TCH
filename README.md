# Taste Match 🎵🎬📚

**Taste Match est le jeu social qui transforme vos films, musiques et livres préférés en un défi amusant et révélateur avec vos amis. Réglez les débats, découvrez des pépites cachées et trouvez qui est votre véritable âme-sœur culturelle.**

Ce projet vise à créer une application sociale engageante où l'interaction principale est un "défi de goût" ludique et direct entre utilisateurs. L'objectif n'est pas seulement de cataloguer des œuvres culturelles, mais de transformer ces catalogues en un jeu interactif, un véritable "démarreur de conversation".

## 📖 Table des matières

- [🎯 À propos du projet](#-à-propos-du-projet)
  - [Proposition de valeur unique](#proposition-de-valeur-unique)
  - [Audience cible](#audience-cible)
- [✨ Fonctionnalités clés](#-fonctionnalités-clés)
- [🛠️ Stack technologique](#stack-technologique)
- [🏗️ Architecture](#architecture)
- [🚀 Feuille de route du projet](#feuille-de-route-du-projet)
- [🔒 Sécurité (Approche DevSecOps)](#sécurité-approche-devsecops)
- [🏁 Démarrage rapide](#démarrage-rapide)
- [📊 Indicateurs clés de performance (KPIs)](#indicateurs-clés-de-performance-kpis)
- [⚖️ Légalité et conformité](#légalité-et-conformité)
- [🤝 Contribution](#contribution)
- [📄 Licence](#licence)
- [🙏 Remerciements](#remerciements)

## 🎯 À propos du projet

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

## ✨ Fonctionnalités clés

- **Parcours d'intégration optimisé :** Un processus d'inscription rapide pour guider l'utilisateur vers son premier "match" le plus vite possible, le "moment Aha!" de l'application.
- **Création de listes expressives :** Les listes sont l'unité de base de la créativité de l'utilisateur. Des fonctionnalités comme les listes collaboratives et les modèles sont prévues.
- **Mécanique de "Match" gamifiée :** Un algorithme calcule un score de compatibilité, enrichi par des éléments de jeu comme des séries (streaks), des badges/succès et des classements entre amis pour encourager l'engagement.
- **Défis de groupe :** Un utilisateur peut défier un groupe entier, avec un écran de résultats affichant le score moyen et les classements individuels.
- **Écran de résultats viral :** Conçu pour être partagé ! Il inclut non seulement le score, mais aussi des visualisations de données (diagramme de Venn) et des aperçus qualitatifs amusants. Il comporte un double appel à l'action crucial : **"Partager votre résultat"** et **"Le défier en retour !"** pour créer une boucle virale.

## 🛠️ Stack technologique

La stack est choisie pour une architecture découplée, moderne et scalable, prête pour une application web interactive.

| Composant              | Technologie                        | Justification                                                                                                 |
| :--------------------- | :--------------------------------- | :------------------------------------------------------------------------------------------------------------ |
| **Framework Backend**  | **Django + Django REST Framework** | Fournit une API REST robuste et sécurisée. DRF est le standard pour construire des API avec Django.           |
| **Framework Frontend** | **React**                          | Crée une interface utilisateur riche, rapide et moderne (Single-Page Application), totalement découplée du backend. |
| **Base de Données**    | **PostgreSQL**                     | Indispensable pour une application sociale, gère une forte concurrence et assure la parité dev/prod.          |
| **Mise en Cache**      | **Redis**                          | Essentiel pour améliorer les performances et respecter les limites de débit des APIs externes.                |
| **File de Tâches**     | **Celery**                         | Permet d'exécuter des tâches longues en arrière-plan pour une expérience utilisateur fluide.                  |
| **Déploiement**        | **Docker + Nginx**                 | Docker conteneurise l'environnement. Nginx sert le frontend React et agit comme reverse proxy pour l'API.     |

## 🏗️ Architecture

L'architecture est découplée (headless), avec un frontend React et un backend Django qui communiquent via une API REST.