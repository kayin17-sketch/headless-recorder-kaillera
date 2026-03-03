#!/bin/bash

echo "================================"
echo "Kaillera Headless Recorder"
echo "================================"
echo ""

cd "$(dirname "$0")/backend"

if [ ! -d "../recordings" ]; then
    echo "Creando directorio de grabaciones..."
    mkdir "../recordings"
fi

echo "Iniciando servidor en http://localhost:8000"
echo "Presiona Ctrl+C para detener"
echo ""

python3 main.py
