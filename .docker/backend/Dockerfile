FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# Copy app (compose will mount volume during dev)
COPY backend /app

EXPOSE 8000

CMD ["bash", "-lc", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

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
