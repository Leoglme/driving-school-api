#!/bin/bash

# Script pour attendre que MariaDB soit prêt
host="$1"
port="$2"
timeout="${3:-30}"  # Temps d'attente maximal en secondes (par défaut 30)

echo "Attente de la disponibilité de $host:$port..."

# Boucle jusqu'à ce que la connexion soit établie ou que le timeout soit atteint
start_time=$(date +%s)
while true; do
    # Tester la connexion au port avec nc (netcat)
    nc -z "$host" "$port" > /dev/null 2>&1
    result=$?

    if [ $result -eq 0 ]; then
        echo "$host:$port est disponible !"
        break
    fi

    current_time=$(date +%s)
    elapsed=$((current_time - start_time))
    if [ $elapsed -ge $timeout ]; then
        echo "Erreur : Timeout après $timeout secondes, impossible de se connecter à $host:$port"
        exit 1
    fi

    echo "En attente de $host:$port... ($elapsed secondes écoulées)"
    sleep 1
done