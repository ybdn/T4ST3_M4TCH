#!/bin/bash
# Script pour démarrer l'environnement de développement local

echo "🚀 Démarrage de l'environnement de développement T4ST3_M4TCH"
echo "=================================================="

# Vérifier que les fichiers de config existent
if [ ! -f "backend/.env.local" ]; then
    echo "❌ Fichier backend/.env.local manquant"
    echo "   Copiez backend/.env.local.example et ajustez les variables"
    exit 1
fi

if [ ! -f "frontend/.env.local" ]; then
    echo "❌ Fichier frontend/.env.local manquant"
    echo "   Copiez frontend/.env.local.example et ajustez les variables"
    exit 1
fi

# Arrêter les services existants
echo "🛑 Arrêt des services existants..."
docker-compose -f docker-compose.local.yml down

# Construire et démarrer les services
echo "🔨 Construction et démarrage des services..."
docker-compose -f docker-compose.local.yml up --build

echo "✅ Environnement de développement démarré !"
echo "🌐 Frontend: http://localhost:3000"
echo "⚡ Backend API: http://localhost:8000"
echo "🗃️  Admin Django: http://localhost:8000/admin/"