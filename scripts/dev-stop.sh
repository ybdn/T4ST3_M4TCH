#!/bin/bash
# Script pour arrêter l'environnement de développement local

echo "🛑 Arrêt de l'environnement de développement T4ST3_M4TCH"
echo "=================================================="

# Arrêter tous les services
docker-compose -f docker-compose.local.yml down

echo "✅ Environnement de développement arrêté !"