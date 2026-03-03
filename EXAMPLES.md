# Ejemplos de Uso

## Iniciar el Servidor

```bash
# Método 1: Usar el script
./start.sh

# Método 2: Ejecutar directamente
cd backend
python3 main.py
```

El servidor estará disponible en `http://localhost:8000`

## Uso de la Interfaz Web

### 1. Configurar y Conectar a un Servidor

1. Abre `http://localhost:8000` en tu navegador
2. En la sección "Servidores Configurados":
   - Nombre: `Mi Servidor Local`
   - Host: `127.0.0.1`
   - Puerto: `27888`
3. Haz clic en "Añadir Servidor"
4. Selecciona el servidor en el menú desplegable
5. Haz clic en "Conectar"

### 2. Unirse a una Partida

1. Verás la lista de partidas disponibles en "Partidas Disponibles"
2. Haz clic en una partida para seleccionarla (se marcará en azul)
3. Haz clic en "Unirse a Partida"
4. Haz clic en "Iniciar Partida"

### 3. Grabar una Partida

1. Una vez en una partida, haz clic en "Iniciar Grabación"
2. Juega normalmente
3. Cuando termines, haz clic en "Detener Grabación"

### 4. Ver y Gestionar Grabaciones

Las grabaciones se muestran en "Grabaciones Guardadas" con:
- Nombre del juego
- ID de grabación
- Duración
- Número de frames
- Fecha y hora
- Servidor

Puedes eliminar grabaciones haciendo clic en el botón "Eliminar".

## API REST - Uso con curl

### Listar Servidores

```bash
curl http://localhost:8000/api/servers
```

### Conectar a un Servidor

```bash
curl -X POST http://localhost:8000/api/connect \
  -H "Content-Type: application/json" \
  -d '{
    "instance_id": "default",
    "host": "127.0.0.1",
    "port": 27888
  }'
```

### Listar Partidas (debes estar conectado)

Las partidas se actualizan automáticamente en la interfaz web.

### Unirse a una Partida

```bash
curl -X POST http://localhost:8000/api/join-game \
  -H "Content-Type: application/json" \
  -d '{
    "instance_id": "default",
    "game_id": 1
  }'
```

### Iniciar una Partida

```bash
curl -X POST http://localhost:8000/api/start-game \
  -H "Content-Type: application/json" \
  -d '{
    "instance_id": "default"
  }'
```

### Iniciar Grabación

```bash
curl -X POST http://localhost:8000/api/start-recording \
  -H "Content-Type: application/json" \
  -d '{
    "instance_id": "default"
  }'
```

### Detener Grabación

```bash
curl -X POST http://localhost:8000/api/stop-recording \
  -H "Content-Type: application/json" \
  -d '{
    "instance_id": "default"
  }'
```

### Listar Grabaciones

```bash
curl http://localhost:8000/api/recordings
```

### Eliminar una Grabación

```bash
curl -X POST http://localhost:8000/api/delete-recording \
  -H "Content-Type: application/json" \
  -d '{
    "recording_id": "20250303_180000"
  }'
```

### Desconectar

```bash
curl -X POST http://localhost:8000/api/disconnect \
  -H "Content-Type: application/json" \
  -d '{
    "instance_id": "default"
  }'
```

## Formatos de Grabación

### Formato JSON

Las grabaciones en JSON incluyen metadatos completos:

```json
{
  "recording_id": "20250303_180000",
  "timestamp": "2025-03-03T18:00:00.000000",
  "server_host": "127.0.0.1",
  "server_port": 27888,
  "game_id": 1,
  "game_name": "Street Fighter II",
  "emulator": "MAME",
  "players": [
    {
      "username": "Player1",
      "ping": 50,
      "connection_type": 3
    }
  ],
  "duration": 120.5,
  "frames": 7200,
  "frame_data": [
    {
      "frame": 0,
      "timestamp": 1234567890.123,
      "player_number": 0,
      "data": "0011223344556677"
    }
  ]
}
```

### Formato Kaillera (.kr)

Formato binario compatible con emuladores Kaillera:

- Header: `KAI` (3 bytes)
- Versión: `0x01` (1 byte)
- Nombre del juego (32 bytes, null-terminated)
- Nombre del emulador (32 bytes, null-terminated)
- Timestamp (64 bytes, UTF-8)
- Game ID (4 bytes, little-endian)
- Duración (4 bytes, little-endian, segundos)
- Número de frames (4 bytes, little-endian)
- Número de jugadores (4 bytes, little-endian)
- Por cada jugador:
  - Username (32 bytes, null-terminated)
  - Ping (4 bytes, little-endian)
  - Connection type (1 byte)
- Por cada frame:
  - Frame number (4 bytes, little-endian)
  - Data length (2 bytes, little-endian)
  - Data (variable length)

## Uso Avanzado

### Múltiples Servidores Simultáneos

Puedes abrir múltiples pestañas del navegador y conectar a diferentes servidores simultáneamente:

```bash
# Pestaña 1: Conectar al servidor local
# http://localhost:8000

# Configura el servidor 1 en la interfaz y conéctate

# Pestaña 2: Conectar a otro servidor
# http://localhost:8000

# Configura el servidor 2 en la interfaz y conéctate
```

Nota: Actualmente, las instancias se gestionan por `instance_id`. Para múltiples conexiones, necesitarías usar diferentes IDs de instancia.

### Automatización con Python

```python
import requests

# Conectar
requests.post('http://localhost:8000/api/connect', json={
    'instance_id': 'instance1',
    'host': '127.0.0.1',
    'port': 27888
})

# Unirse a partida
requests.post('http://localhost:8000/api/join-game', json={
    'instance_id': 'instance1',
    'game_id': 1
})

# Iniciar partida
requests.post('http://localhost:8000/api/start-game', json={
    'instance_id': 'instance1'
})

# Grabar durante 60 segundos
requests.post('http://localhost:8000/api/start-recording', json={
    'instance_id': 'instance1'
})

import time
time.sleep(60)

requests.post('http://localhost:8000/api/stop-recording', json={
    'instance_id': 'instance1'
})
```

### Reproducir una Grabación

El proyecto actualmente solo graba partidas. Para reproducirlas, necesitarías:

1. Un emulador compatible con Kaillera
2. Convertir el formato de grabación al formato del emulador
3. Cargar el archivo de replay en el emulador

Esto requeriría desarrollo adicional específico para cada emulador.

## Troubleshooting

### Error: "No puedo conectar al servidor"

```bash
# Verificar que el servidor Kaillera esté corriendo
netstat -an | grep 27888

# Si no está corriendo, inicia un servidor Kaillera
# Ejemplo con Direlera-rs:
cd direlera-rs
./direlera-rs
```

### Error: "Las grabaciones no se guardan"

```bash
# Verificar permisos
ls -la recordings/

# Crear directorio si no existe
mkdir -p recordings
chmod 755 recordings
```

### Puerto 8000 ya en uso

```bash
# Cambiar el puerto en backend/main.py
# run_server(host='0.0.0.0', port=8080)  # Cambiar a 8080

# O matar el proceso que usa el puerto
lsof -i :8000
kill -9 <PID>
```

## Consejos de Uso

1. **Configura bien la red**: Asegúrate de tener baja latencia con el servidor Kaillera
2. **Usa conexiones cableadas**: WiFi puede causar lag en las grabaciones
3. **Monitorea el ping**: Un ping alto puede afectar la calidad de la grabación
4. **Espacio en disco**: Las grabaciones pueden ocupar bastante espacio, especialmente para partidas largas
5. **Nombra bien las partidas**: Te ayudará a identificar las grabaciones después

## Recursos Adicionales

- [Protocolo Kaillera](https://kaillerareborn.github.io/resources/kailleraprotocol.txt)
- [Kaillera Reborn](https://kaillerareborn.github.io)
- [Direlera-rs](https://github.com/caromdreamer/direlera-rs)
