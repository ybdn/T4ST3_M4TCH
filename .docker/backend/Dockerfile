FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY backend/ .

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput || echo "Static files collection skipped"

# Port d'exposition
EXPOSE 8000

# Commande de démarrage pour la production
CMD ["python", "manage.py", "migrate", "&&", "gunicorn", "--bind", "0.0.0.0:8000", "tastematch_api.wsgi:application"]
