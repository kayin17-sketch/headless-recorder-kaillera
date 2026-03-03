#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.server import run_server

if __name__ == '__main__':
    print("=" * 50)
    print("Kaillera Headless Recorder")
    print("=" * 50)
    print()
    print("Este es un cliente headless para grabar partidas de Kaillera")
    print("con una interfaz web moderna.")
    print()
    print("El servidor se iniciará en http://localhost:8000")
    print()
    print("Presiona Ctrl+C para detener el servidor.")
    print("=" * 50)
    print()
    
    try:
        run_server(host='0.0.0.0', port=8000)
    except KeyboardInterrupt:
        print("\nServidor detenido.")
