# Utiliser une image Node.js officielle
FROM node:20-alpine

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY ./frontend/package.json ./frontend/package-lock.json* ./

# Installer les dépendances
RUN npm install

# Copier le code source de l'application
COPY ./frontend /app/

# Exposer le port de développement
EXPOSE 3000

# Commande pour démarrer le serveur de développement
CMD ["npm", "run", "dev"]