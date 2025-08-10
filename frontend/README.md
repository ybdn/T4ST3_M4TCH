# Taste Match Frontend

## 🎨 Charte graphique et Design System (v2)

Style global: **noir et blanc épuré**, inspiré de X.com avec effets de verre opaque et micro-interactions subtiles.

### Palette révisée

#### Couleurs principales

- **Fond principal**: `#000000` (noir pur)
- **Surfaces**: `#202327` (noir-gris)
- **Texte principal**: `#ffffff` (blanc pur)
- **Texte secondaire**: `#e7e9ea` (blanc cassé)
- **Texte muted**: `#71767b` (gris moyen)

#### Accent et interactions

- **Primaire**: `#e11d48` (rose néon) - pour CTAs et éléments importants
- **Bordures**: `rgba(255,255,255,0.08)` (blanc transparent)
- **Effets de verre premium**:
  - Verre translucide: `rgba(255,255,255,0.05)` à `rgba(255,255,255,0.15)` avec backdrop-blur
  - Bordures lumineuses: `rgba(255,255,255,0.20)` à `rgba(255,255,255,0.40)`
  - Reflets internes: `rgba(255,255,255,0.15)` à `rgba(255,255,255,0.30)`
  - Saturation: `180%` pour intensifier les couleurs à travers le verre

#### Usage des couleurs

- **Titres**: Blanc pur (`text-white`) - pas de gradients
- **Corps de texte**: Blanc cassé (`text-tm-text`)
- **Éléments secondaires**: Gris moyen (`text-tm-text-muted`)
- **Accents**: Rose néon parcimonieux (`text-tm-primary`)

#### Classes CSS spécialisées

- **`.tm-glass`**: Verre léger pour petits éléments
- **`.tm-glass-card`**: Verre renforcé pour cartes principales
- **`.tm-glass-input`**: Optimisé pour les champs de saisie
- **`.tm-glass-button`**: Boutons avec effets vitreux premium

Ces couleurs sont configurées dans `tailwind.config.cjs` avec le préfixe `tm-` pour éviter les collisions.

## 📐 Système de proportions dorées (φ ≈ 1.618)

**Philosophie**: Toute l'application utilise les proportions basées sur le nombre d'or pour créer une harmonie visuelle mathématiquement parfaite.

### Échelle typographique dorée

- **`.phi-title`**: `2.618rem` (≈42px) - Titres principaux comme "T4ST3 M4TCH"
- **`.phi-subtitle`**: `1.618rem` (≈26px) - Sous-titres et titres secondaires
- **`.phi-label`**: `0.875rem` (14px) - Labels de formulaires
- **`.phi-description`**: `0.75rem` (12px) - Textes d'aide et descriptions
- **Line-height**: `1.618` pour les titres, `1.414` (√2) pour l'équilibre du corps de texte

### Dimensions et espacements dorés

#### Conteneurs

- **`.phi-container`**: `25.888rem` (≈415px) - Largeur optimale des
  formulaires

#### Éléments d'interaction

- **`.phi-input`**: Hauteur `3.236rem` (≈52px), padding `0.764rem × 1.236rem`
- **`.phi-button`**: Hauteur `3.236rem`, padding `0.764rem × 1.618rem`

#### Cartes et surfaces

- **`.phi-card`**: Padding `2.618rem` (≈42px) - Cartes principales
- **`.phi-small-card`**: Padding `1.618rem` (≈26px) - Cartes secondaires

#### Espacements systémiques

- **`.phi-gap`**: `1.618rem` - Espacement principal entre sections
- **`.phi-gap-small`**: `1rem` - Espacement secondaire
- **`.phi-gap-mini`**: `0.618rem` - Micro-espacements pour éléments proches

### Typographie épurée

- **Branding titres**: font-cinzel, toujours en blanc (`text-white`) avec classes `.phi-title/.phi-subtitle`
- **Interface utilisateur**: font-inter, 400/600/700 (lisible, moderne)
- **Boutons**: font-semibold, classes `.phi-button`
- **Labels/descriptions**: classes `.phi-label/.phi-description` avec couleurs nuancées

**Règle fondamentale**: Tous les éléments respectent les proportions φ pour une harmonie visuelle optimale.

Les polices sont importées dans `index.css` et les proportions dorées configurées avec classes `.phi-*`.

### Ombres

- Ombre: `0 10px 30px rgba(0,0,0,0.35)` (classe `shadow-lg` de Tailwind)

### Composants UI

- `AppHeader`: AppBar gradient sombre + blur, titre en gradient rose→bleu, slot retour et actions.
- `AppBottomNav`: icônes outlined → filled à la sélection, fond translucide, labels visibles.
- `Paper`/`Card`: surfaces sombres, bords nets (angles à 90°), léger gradient de surface.

Ces composants sont construits avec des `div` standards et stylisés via Tailwind CSS.

### Mécanismes d’interaction

- Sélection bottom nav: légère élévation (`transform -translate-y-0.5`).
- Icônes d’édition/suppression: survol avec teinte d’accent et léger scale (`hover:scale-105`).

### Assets visuels

- Arrière-plan: dégradés radiaux discrets rose/bleu (voir `src/index.css`).

## 📦 Implémentation technique

### Stack Frontend

- **React 19** + **TypeScript**: Base de l'application avec typage strict
- **Vite**: Build tool et serveur de développement rapide
- **React Router DOM**: Navigation côté client
- **Tailwind CSS 3.4**: Framework CSS utilitaire pour le styling
- **Headless UI 2.2**: Composants UI accessibles sans styling (Transitions, etc.)
- **Axios**: Client HTTP pour les appels API
- **Clsx**: Utilitaire pour la gestion conditionnelle des classes CSS

### Architecture CSS

- **Design System**: Basé sur Tailwind avec palette personnalisée (tm-\*)
- **Component Pattern**: Composants réutilisables avec classes Tailwind
- **Responsive Design**: Mobile-first avec breakpoints Tailwind
- **Dark Theme**: Thème sombre unique avec effets de verre (backdrop-blur)

### Variables CSS

Définies dans `src/index.css` (`--tm-*`) pour les valeurs globales comme les gradients, qui sont ensuite utilisées dans la configuration de Tailwind.

### Layout commun

- Header et bottom nav factorisés:
  - `src/components/AppHeader.tsx`
  - `src/components/AppBottomNav.tsx`

### Pages refactorées

- `HomePage`, `ExplorePage`, `ListsPage`, `MatchPage`, `components/Dashboard` utilisent désormais les composants communs et le thème sombre via Tailwind.

## 🧩 Guidelines d’usage

### Couleurs

- Utiliser les classes Tailwind: `bg-primary`, `text-secondary`, `border-tm-border`.
- Pour les gradients ou cas spécifiques, utiliser les variables CSS: `var(--tm-gradient)`.

### Styles de texte

- Appliquer les classes de police et de taille de Tailwind: `font-cinzel`, `font-inter`, `text-lg`, `font-bold`.

### Espacement

- Utiliser les classes d'espacement de Tailwind: `p-4`, `m-2`, `gap-4`.
- Pour le design responsive, utiliser les préfixes de Tailwind: `md:p-8`, `lg:gap-6`.

### Accessibilité

- Toujours renseigner `aria-label` sur les éléments interactifs sans texte (boutons avec icônes).
- Utiliser les utilitaires `focus:` de Tailwind pour assurer des états de focus clairs.

## 🌐 Connexion au Backend et Déploiement

\n### Communication avec l'API
Le frontend est découplé du backend et communique avec lui via des appels à une API REST. L'adresse de base de cette API est configurable via une variable d'environnement pour s'adapter à différents environnements (local, production).

La logique de configuration se trouve dans `src/config.ts` et se base sur la variable `VITE_API_URL` fournie par Vite.

\n### Développement Local
Pour le développement local, le frontend doit pointer vers l'API qui tourne sur `localhost:8000`. Le code utilise cette adresse par défaut si `VITE_API_URL` n'est pas définie.

Il est recommandé de créer un fichier `.env.local` à la racine du dossier `frontend/` pour spécifier explicitement l'URL :

Fichier `frontend/.env.local` : `VITE_API_URL="http://localhost:8000"`

\n### Environnement de Production (Render)
Lorsque le frontend est déployé sur Render, il doit connaître l'adresse publique du service backend.
\n1. Allez dans les paramètres de votre service **frontend** sur Render. 2. Cliquez sur la section **"Environment"**. 3. Ajoutez ou modifiez la variable d'environnement :

- **Key :** `VITE_API_URL`
- **Value :** `https://tastematch-api.onrender.com` (ou l'URL publique de votre service backend).

\n### Déploiement
Le service est déployé sur Render. Pour la configuration d'un nom de domaine personnalisé, veuillez vous référer à la section `🌐 Déploiement et Environnement de Production` dans le `README.md` principal à la racine du projet.

## 🚀 Démarrage

1. Installer les dépendances: `npm install`
2. Lancer le serveur de développement: `npm run dev`

## 📁 Arborescence

src/
├── components/ # Composants réutilisables
│ ├── AppBottomNav.tsx
│ ├── AppHeader.tsx
│ └── ...
├── pages/ # Vues principales de l'application
│ ├── HomePage.tsx
│ └── ...
├── context/ # Contexte React (ex: Auth, Feedback)
├── hooks/ # Hooks personnalisés
├── services/ # Logique métier, appels API
├── main.tsx # Point d'entrée de l'application
└── index.css # Styles globaux et variables CSS

## 🧪 Bonnes pratiques UI/UX

- Focus clair: header minimal, actions contextualisées.
- Feedback immédiat: states loading/success/error visibles (géré par `UserFeedback.tsx`).
- Gestuelle cohérente mobile: bottom nav persistante, header sticky.

## 🎯 Guidelines pour l'application entière

### ✅ Règles d'or obligatoires

#### Proportions et dimensions

- **TOUJOURS** utiliser les classes `.phi-*` pour toutes les dimensions
- **Conteneurs**: `.phi-container` pour largeurs optimales
- **Espacements**: `.phi-gap`, `.phi-gap-small`, `.phi-gap-mini` uniquement
- **Cartes**: `.phi-card` ou `.phi-small-card` selon l'importance

#### Typographie harmonieuse

- **Titres principaux**: `.phi-title` + `font-cinzel` + `text-white`
- **Sous-titres**: `.phi-subtitle` + `font-cinzel` + `text-tm-text`
- **Labels**: `.phi-label` + `font-inter` + `text-tm-text`
- **Descriptions**: `.phi-description` + `font-inter` + `text-tm-text-muted`

#### Effets de verre systématiques

- **Éléments principaux**: `.tm-glass-card` pour profondeur maximum
- **Éléments secondaires**: `.tm-glass` pour légèreté
- **Inputs/formulaires**: `.tm-glass-input` optimisé pour la saisie
- **Boutons CTAs**: `.tm-glass-button` avec effets premium

### ❌ Interdictions absolues

#### Proportions et mesures

- **Jamais** de valeurs arbitraires (px, rem non-φ)
- **Jamais** `space-y-*`, `p-*`, `m-*` classiques → Utiliser `.phi-*`
- **Jamais** `max-w-md`, `max-w-lg` → Utiliser `.phi-container`

#### Styles visuels

- **Jamais** de gradients sur les titres → Blanc pur uniquement
- **Jamais** de couleurs pleines → Toujours effets de verre translucides
- **Jamais** d'icônes décoratives au-dessus des titres
- **Jamais** de rounded-\* autre que `rounded-xl`

### 🔧 Migration des pages existantes

#### Checklist de migration obligatoire

- [ ] **Classes `.phi-*`**: Remplacer tous les espacements par proportions dorées
- [ ] **Typographie dorée**: Convertir vers l'échelle `.phi-title/.phi-subtitle/.phi-label`
- [ ] **Effets de verre**: Appliquer `.tm-glass-*` appropriés selon le contexte
- [ ] **Conteneurs**: Vérifier largeurs avec `.phi-container`
- [ ] **Interactions**: Tester focus/hover/active avec contours blancs
- [ ] **Hiérarchie**: Valider progression visuelle harmonieuse
- [ ] **Cohérence**: Aucun élément sans classe `.phi-*` ou `.tm-glass-*`

#### Pages prioritaires à migrer

1. **HomePage** - Dashboard principal avec cartes de listes
2. **ExplorePage** - Navigation et recherche avec suggestions
3. **ListsPage** - Gestion des listes avec formulaires
4. **MatchPage** - Interface de matching avec cartes interactives
5. **QuickAddPage** - Ajout rapide avec recherche externe

**Objectif final**: Cohérence visuelle parfaite sur toute l'application avec harmonie mathématique φ.

### Échelle d’espacement (reco)

- Utiliser l'échelle par défaut de Tailwind (multiple de 4px).

### Motion (micro-interactions)

- Utiliser les classes de transition de Tailwind (`duration-200`, `ease-out`).
- Pour les animations complexes, utiliser la librairie Headless UI.

### Icônes

- Utiliser des composants SVG et les styliser avec les classes de Tailwind (`h-6 w-6`, `text-primary`).

### Do / Don’t

#### ✅ Do

- **Titres**: font-cinzel en blanc pur (`text-white`)
- **Surfaces**: Effets de verre avec backdrop-blur
- **Accents**: Rose néon parcimonieux et stratégique
- **Espacement**: Généreux, aéré (p-6, p-8)
- **Bordures**: Subtiles, blanches transparentes

#### ❌ Don't

- **Gradients sur les titres**: Gardez les titres en blanc simple
- **Icônes décoratives**: Évitez les icônes au-dessus des titres
- **Couleurs vives**: Hors palette noir/blanc/rose
- **Arrondis excessifs**: Utilisez rounded-xl maximum
- **Ombres lourdes**: Préférez les effets de transparence

## 🗒️ Changelog UI / Thème

### v2.4 (Harmonie dorée et verre premium)

- **🏆 SYSTÈME DE PROPORTIONS DORÉES**: Toute l'UI basée sur φ ≈ 1.618
- **📐 Classes `.phi-*`**: Échelle typographique et spatiale mathématiquement parfaite
- **🪟 Effets de verre premium**: Transparence blanche, reflets, saturation 180%
- **✨ Boutons vitreux**: `.tm-glass-button` avec gradients et interactions premium
- **📏 Conteneurs optimaux**: `.phi-container` pour largeurs harmonieuses
- **🎨 Guidelines complètes**: Documentation pour migration de toute l'app

### v2.3 (Design épuré noir et blanc)

- **Palette révisée**: Noir et blanc épuré, sans gradients sur les titres
- **Suppression des icônes décoratives**: Interface minimaliste et focus contenu
- **Effets de verre opaque**: Classes `.tm-glass` et `.tm-glass-card` avec backdrop-blur
- **Pages d'authentification**: Arrière-plans avec dégradés radiaux discrets
- **Titres en blanc pur**: font-cinzel, `text-white`, pas de gradient
- **Composants Headless UI**: Field, Label, Input, Button avec styling glass

### v2.2 (Migration Headless UI complète)

- **Migration complète vers Headless UI + Tailwind CSS**
- Suppression totale de Material-UI (@mui/material, @mui/icons-material)
- Architecture CSS 100% Tailwind avec design system personnalisé (tm-\*)
- Composants intégralement refactorisés : AppHeader, AppBottomNav, UserFeedback
- Thème sombre premium avec effets de verre (backdrop-blur-xl)
- Stack moderne : React 19, Vite, TypeScript, Headless UI 2.2, Tailwind CSS 3.4

### v2.1 (néon sombre épuré)

- Stack technique migrée vers Tailwind CSS et Headless UI. Thème sombre, Inter + Cinzel, header/nav translucides, icônes outlined/filled, cards à angles nets (0px radius) et gradient léger.

## 📴 Features actuellement désactivées (stubs)

Ces fonctionnalités ont été temporairement mises en stubs pour stabiliser la base (build propre, zéro dette TS) avant réintégration incrémentale.

| Domaine      | Élément                                         | Statut                                                  | Fichier(s) concerné(s)                                | Plan de réactivation                                                          |
| ------------ | ----------------------------------------------- | ------------------------------------------------------- | ----------------------------------------------------- | ----------------------------------------------------------------------------- |
| Social       | Profil (édition)                                | Désactivé (lecture si profil existe, sinon placeholder) | `components/SocialProfile.tsx`, `hooks/useSocial.ts`  | Réimplémenter fetch profil + mutation backend, réactiver états d'édition      |
| Social       | Liste d'amis (requêtes / ajout réel)            | Simplifié (affichage liste vide)                        | `components/FriendsManager.tsx`, `hooks/useSocial.ts` | Rebrancher endpoints friends + friendRequests, réintroduire onglets & actions |
| Social       | Friend requests                                 | Supprimé                                                | `components/FriendsManager.tsx`                       | Restaurer sous forme de second Tab avec mapping `friendRequests`              |
| Versus       | Matchs & challenges                             | Stub très minimal                                       | `components/VersusMatch-simple.tsx`                   | Recréer logique de session + API versus, scores temps réel                    |
| Match Global | API étendue (reco filtrées, pagination avancée) | Réduit au strict minimum                                | `services/matchApi.ts`                                | Réintroduire endpoints (pagination, catégories, stats) avec typage progressif |

### Objectifs de réactivation progressive

1. Réintroduire le profil social en lecture seule réelle (GET /profile)
2. Ajouter mutation du profil (PATCH /profile) avec validation optimiste
3. Rebrancher friends list (GET /friends) puis requests (GET /friend-requests)
4. Activer actions add / accept / decline avec toasts unifiés
5. Implémenter Versus (phases: création, rounds, scoring, historique)

### Principes durant la réactivation

- Chaque étape doit conserver le build sans erreur TypeScript
- Couvrir les formes de données réintroduites avec types isolés puis mutualiser
- Ajouter tests unitaires légers (hooks/services) avant d'étendre le périmètre
- Pas de réintroduction massive: feature flags ou garde-fous conditionnels

\n### Notes techniques sur les stubs
`hooks/useSocial.ts` retourne des valeurs null / arrays vides mais déjà typées pour minimiser les changements côté composants. Lors de la réactivation, remplacer progressivement les stubs par des hooks réels, idéalement en conservant la même surface API pour éviter des refactors UI.

---

Dernière mise à jour de cette section: (placeholder – mettre à jour lors de la première réactivation sociale)
