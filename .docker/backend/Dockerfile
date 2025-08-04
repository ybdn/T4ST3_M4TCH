# Utiliser une image Python officielle
FROM python:3.11-slim

# Définir les variables d'environnement
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances
COPY ./backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source de l'application
COPY ./backend /app/
