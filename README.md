
# **Taste Match 🎵🎬📚**

**Taste Match est le jeu social qui transforme vos films, musiques et livres préférés en un défi amusant et révélateur avec vos amis. Réglez les débats, découvrez des pépites cachées et découvrez qui est votre véritable âme-sœur culturelle.**

Ce projet a pour ambition de créer une application sociale engageante où l'interaction principale est un "défi de goût" ludique et direct entre utilisateurs. L'objectif n'est pas seulement de cataloguer des œuvres culturelles, mais de transformer ces catalogues en un jeu interactif, un véritable "démarreur de conversation".

## **📖 Table des matières**

* [🎯 À propos du projet](https://www.google.com/search?q=%23-%C3%A0-propos-du-projet)  
  * [Proposition de valeur unique](https://www.google.com/search?q=%23proposition-de-valeur-unique)  
  * [Audience cible](https://www.google.com/search?q=%23audience-cible)  
* [✨ Fonctionnalités clés](https://www.google.com/search?q=%23-fonctionnalit%C3%A9s-cl%C3%A9s)  
* [🛠️ Stack technologique](https://www.google.com/search?q=%23%EF%B8%8F-stack-technologique)  
* [🏗️ Architecture](https://www.google.com/search?q=%23%EF%B8%8F-architecture)  
* [🚀 Feuille de route du projet](https://www.google.com/search?q=%23-feuille-de-route-du-projet)  
* [🔒 Sécurité (Approche DevSecOps)](https://www.google.com/search?q=%23-s%C3%A9curit%C3%A9-approche-devsecops)  
* [🏁 Démarrage rapide](https://www.google.com/search?q=%23-d%C3%A9marrage-rapide)  
* [📊 Indicateurs clés de performance (KPIs)](https://www.google.com/search?q=%23-indicateurs-cl%C3%A9s-de-performance-kpis)  
* [⚖️ Légalité et conformité](https://www.google.com/search?q=%23%EF%B8%8F-l%C3%A9galit%C3%A9-et-conformit%C3%A9)  
* [🤝 Contribution](https://www.google.com/search?q=%23-contribution)  
* [📄 Licence](https://www.google.com/search?q=%23-licence)  
* [🙏 Remerciements](https://www.google.com/search?q=%23-remerciements)

## **🎯 À propos du projet**

Taste Match est né d'un constat simple : les plateformes culturelles existantes comme Letterboxd ou Goodreads sont excellentes pour le catalogage passif, mais manquent d'interaction sociale directe, synchrone et ludique. Taste Match comble cette lacune en ne se contentant pas de permettre la comparaison, mais en la **provoquant** à travers un défi.

Le cœur de l'expérience est le moment de la "révélation" du score de compatibilité, conçu pour susciter une réaction émotionnelle et lancer une conversation : la surprise, la validation ou le débat amical.

### **Proposition de valeur unique**

Taste Match se différencie du paysage concurrentiel sur plusieurs points clés :

* **Actif vs. Passif :** L'application crée des défis interactifs plutôt que de simplement afficher des listes.  
* **Ludique vs. Archivage :** C'est un jeu, pas une simple base de données. L'objectif est le "match".  
* **Révélation Synchrone vs. Navigation Asynchrone :** La magie réside dans la découverte simultanée et partagée des résultats.

### **Audience cible**

La conception s'adresse à plusieurs types d'utilisateurs :

1. **Le Couple Décontracté (Alex & Ben) :** Cherche des moyens amusants de se connecter et de décider quoi regarder ou écouter.  
2. **La Cinéphile Passionnée (Chloé) :** Utilise l'application pour démontrer son expertise et défier les membres de son ciné-club avec des listes pointues.  
3. **L'Organisatrice Sociale (Maria) :** Gère des clubs (lecture, jeux) et utilise l'application pour engager sa communauté et prendre des décisions de groupe.

## **✨ Fonctionnalités clés**

* **Parcours d'intégration optimisé :** Un processus d'inscription rapide pour guider l'utilisateur vers son premier "match" le plus vite possible, le "moment Aha\!" de l'application.  
* **Création de listes expressives :** Les listes sont l'unité de base de la créativité de l'utilisateur. Des fonctionnalités comme les listes collaboratives et les modèles sont prévues.  
* **Mécanique de "Match" gamifiée :** Un algorithme calcule un score de compatibilité, enrichi par des éléments de jeu comme des séries (streaks), des badges/succès et des classements entre amis pour encourager l'engagement.  
* **Défis de groupe :** Un utilisateur peut défier un groupe entier, avec un écran de résultats affichant le score moyen et les classements individuels.  
* **Écran de résultats viral :** Conçu pour être partagé \! Il inclut non seulement le score, mais aussi des visualisations de données (diagramme de Venn) et des aperçus qualitatifs amusants. Il comporte un double appel à l'action crucial : **"Partager votre résultat"** et **"Le défier en retour\!"** pour créer une boucle virale.

## **🛠️ Stack technologique**

La stack a été choisie pour la **scalabilité, la sécurité et la rapidité de développement**, en suivant les recommandations d'experts pour construire un produit prêt pour la production.

| Composant | Technologie | Justification |
| :---- | :---- | :---- |
| **Framework Backend** | **Django** | Fournit une base robuste et sécurisée avec "piles incluses" (Authentification, ORM, Admin), idéale pour les applications sociales et prouvée à grande échelle (ex: Instagram). |
| **Base de Données** | **PostgreSQL** | Indispensable pour une application sociale. Gère une forte concurrence en écriture (contrairement à SQLite), offre des types de données riches et assure la parité dev/prod. |
| **Mise en Cache** | **Redis** | Essentiel pour améliorer les performances de manière drastique et respecter les limites de débit des APIs externes en mettant en cache les requêtes fréquentes. |
| **File de Tâches** | **Celery** | Permet d'exécuter des tâches longues (notifications, calculs) en arrière-plan pour garantir une expérience utilisateur fluide et réactive. |
| **Déploiement** | **Docker** | Conteneurise l'ensemble de l'environnement pour une configuration de développement reproductible, stable et en une seule commande, éliminant les problèmes de "ça marche sur ma machine". |
| **Frontend** | **HTML/CSS/JS** | Une approche simple et efficace via le système de templates de Django, suffisante pour le MVP et évitant une complexité initiale superflue. |

## **🏗️ Architecture**

L'architecture est conçue pour être modulaire, résiliente et scalable.

                    \+-------------------------+  
Utilisateur \----\>  | Navigateur Web (Client) |  
                    \+-------------------------+  
                                | (Requête HTTP)  
                                v  
\+-------------------------------------------------------------+  
|                     Serveur / Backend                        |  
|                                                              |  
|  \+-----------------+       \+----------------+       \+---------+  
|  |   Serveur Web   |  \<--\> |  App Django    | \<--\> |  Cache  |  
|  |    (Gunicorn)   |         |   (Logique)    |        | (Redis) |  
|  \+-----------------+       \+-------+--------+       \+----+----+  
|                                      |                         | (API Cache)  
| (Lecture/Écriture)                   | (Lecture/Écriture)      |  
|   v                                  v                         v  
| \+-----------------+        \+-----------------+      \+----------------+  
| | File de tâches  |          | Base de Données |      |  APIs Externes  |  
| |    (Celery)     |          |  (PostgreSQL)   |      | (TMDb, Spotify) |  
| \+-----------------+        \+-----------------+      \+----------------+  
|        ^                                                          |  
|        | (Tâches Asynchrones)                                     |  
|        |                                                          |  
|  \+-----------------+                                             |  
|  |  Worker Celery   | \-------------------------------------------+  
|  \+-----------------+  (Ex: Envoi de notifications, etc.)         |  
|                                                                   |  
\+------------------------------------------------------------------+

* **Couche de Service API :** Un module dédié gère toutes les interactions avec les APIs externes pour centraliser la logique et la gestion des erreurs.  
* **Traitement Asynchrone :** Celery et Redis sont utilisés pour décharger les tâches longues (comme l'envoi d'emails) de la requête principale, assurant que l'interface utilisateur ne soit jamais bloquée.

## **🚀 Feuille de route du projet**

Le développement est séquencé pour livrer de la valeur rapidement tout en construisant une base solide.

### **Sprint 0 : Fondations professionnelles**

L'objectif est de mettre en place un environnement de développement stable et reproductible avec Docker, d'initialiser le projet Django et de sécuriser les clés d'API.

### **Sprints MVP : Développement des fonctionnalités de base**

1. **Gestion des utilisateurs :** Inscription, connexion, profil.  
2. **Création de listes :** Ajout/suppression d'éléments culturels via les APIs.  
3. **Mécanique de match :** Logique de défi et de calcul du score.  
4. **Résultats et partage :** Écran de résultats viral.

### **Phase 2 : Communauté et engagement (Mois 1-3 post-lancement)**

* Profils utilisateurs publics  
* Fil d'activité global  
* Commentaires et réactions  
* Groupes persistants (clubs)

### **Phase 3 : Découverte et Monétisation (Mois 4-9 post-lancement)**

* Moteur de recommandation simple  
* Niveau "Pro" (Freemium) avec statistiques avancées  
* Marketing d'affiliation sur les œuvres présentées

## **🔒 Sécurité (Approche DevSecOps)**

La sécurité n'est pas une réflexion après coup, mais une pratique continue intégrée dans chaque sprint. Nous nous basons sur le **Top 10 de l'OWASP** comme guide.

| Sprint | Risques pertinents | Actions de sécurité |
| :---- | :---- | :---- |
| **Utilisateurs** | Défaillances d'authentification, Rupture de contrôle d'accès | Hachage de mot de passe fort (Argon2), limitation de débit sur les tentatives de connexion. |
| **Listes** | Injection (SQL), Mauvaise configuration de sécurité | Utilisation exclusive de l'ORM Django, assainissement des entrées utilisateur (prévention XSS). |
| **Matchs** | Rupture de contrôle d'accès | Vérification systématique que les actions sont effectuées par des utilisateurs autorisés sur leurs propres objets. |
| **Tous** | Composants vulnérables et obsolètes | Scan automatisé des dépendances (ex: pip-audit) pour détecter et corriger les vulnérabilités. |

## **🏁 Démarrage rapide**

Pour lancer l'environnement de développement local, assurez-vous d'avoir **Git** et **Docker** (avec Docker Compose) installés sur votre machine.

1. **Clonez le dépôt :**  
   git clone https://github.com/ybdn/taste-match.git  
   cd taste-match

2. Configurez les variables d'environnement :  
   Créez un fichier .env à la racine du projet en copiant le modèle .env.example.  
   cp .env.example .env

   Ouvrez le fichier .env et remplissez les clés API que vous avez obtenues (TMDb, Spotify, etc.) et les autres configurations. **Ce fichier est ignoré par Git et ne doit jamais être partagé.**  
3. Lancez l'application avec Docker Compose :  
   Cette commande unique va construire les images, démarrer tous les conteneurs (Django, PostgreSQL, Redis, Celery), et les lier entre eux.  
   docker-compose up \--build

4. Appliquez les migrations de la base de données :  
   Dans un autre terminal, une fois les conteneurs lancés, exécutez les migrations initiales de Django.  
   docker-compose exec web python manage.py migrate

🎉 Votre environnement de développement Taste Match est maintenant accessible à l'adresse http://localhost:8000 \!

## **📊 Indicateurs clés de performance (KPIs)**

Le succès du projet sera mesuré à l'aide des indicateurs suivants :

* **Engagement :**  
  * Utilisateurs Actifs Quotidiens/Mensuels (DAU/MAU)  
  * Taux de complétion des matchs  
* **Rétention :**  
  * Rétention à J1, J7, J30 (le plus critique)  
  * Taux de désabonnement (Churn Rate)  
* **Viralité :**  
  * Taux de partage des résultats  
  * Coefficient viral (k-factor)

## **⚖️ Légalité et conformité**

Une attention particulière est portée à la conformité légale dès le début du projet.

* **Documents légaux :** Des Conditions d'Utilisation et une Politique de Confidentialité claires seront rédigées pour protéger l'utilisateur et le développeur.  
* **Conformité RGPD :** L'application est développée en tenant compte des principes du RGPD, notamment la minimisation des données et le "droit à l'oubli", qui sera une fonctionnalité technique permettant aux utilisateurs de supprimer leurs données.  
* **Conditions des APIs :** Les exigences d'attribution des fournisseurs de données (comme le logo TMDb) seront respectées dans l'interface utilisateur.

## **🤝 Contribution**

Les contributions sont ce qui fait de la communauté open source un endroit extraordinaire pour apprendre, inspirer et créer. Toutes les contributions que vous apporterez sont **grandement appréciées**.

Si vous avez une suggestion pour améliorer ce projet, veuillez forker le dépôt et créer une pull request. Vous pouvez aussi simplement ouvrir une issue avec le tag "enhancement".

1. Forkez le projet  
2. Créez votre branche de fonctionnalité (git checkout \-b feature/AmazingFeature)  
3. Commitez vos changements (git commit \-m 'Add some AmazingFeature')  
4. Poussez vers la branche (git push origin feature/AmazingFeature)  
5. Ouvrez une Pull Request

## **📄 Licence**

Ce projet est distribué sous la Licence MIT. Voir le fichier LICENSE pour plus d'informations.

## **🙏 Remerciements**

Ce projet n'existerait pas sans les données fantastiques fournies par les APIs suivantes :

* [The Movie Database (TMDb)](https://www.themoviedb.org/)  
* [Spotify for Developers](https://developer.spotify.com/)  
* [Google Books APIs](https://developers.google.com/books)  
* [IGDB API](https://api-docs.igdb.com/)
