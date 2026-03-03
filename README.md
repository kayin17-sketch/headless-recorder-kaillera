# Kaillera Headless Recorder

Un cliente headless lightweight para grabar partidas de Kaillera con una interfaz web moderna.

## Características

- **Cliente Headless**: Conecta a servidores Kaillera sin necesidad de un emulador gráfico
- **Interfaz Web**: Panel de control moderno accesible desde cualquier navegador
- **Grabación de Partidas**: Guarda partidas en formato JSON y formato Kaillera nativo (.kr)
- **Gestión de Servidores**: Configura múltiples servidores para monitorear
- **Monitoreo en Tiempo Real**: Visualiza partidas activas y estado de conexión

## Arquitectura

```
headless_recorder_kaillera/
├── backend/
│   ├── protocol/
│   │   ├── kaillera_protocol.py  # Implementación del protocolo Kaillera
│   │   └── kaillera_client.py   # Cliente para conectar a servidores
│   ├── recorder/
│   │   └── recorder.py          # Sistema de grabación de partidas
│   ├── api/
│   │   └── server.py            # Servidor HTTP con API REST
│   └── main.py                 # Punto de entrada
├── frontend/
│   ├── templates/
│   │   └── index.html           # Interfaz web
│   └── static/
│       ├── style.css            # Estilos
│       └── app.js               # Lógica del frontend
└── recordings/                  # Directorio de grabaciones
```

## Requisitos

- Python 3.7 o superior
- Servidor Kaillera (puedes usar [EmuLinker-K](https://github.com/hopskipnfall/EmuLinker-K) o [Direlera-rs](https://github.com/caromdreamer/direlera-rs))

## Instalación

1. Clona o descarga este repositorio:
```bash
cd headless_recorder_kaillera
```

2. El proyecto usa solo librerías estándar de Python, no requiere instalación de dependencias.

## Uso

### Iniciar el Servidor

```bash
cd backend
python3 main.py
```

El servidor se iniciará en `http://localhost:8000`

### Usar la Interfaz Web

1. Abre tu navegador y visita `http://localhost:8000`

2. **Configurar Servidores**:
   - Añade el host y puerto de tu servidor Kaillera
   - Ejemplo: Host `127.0.0.1`, Puerto `27888`

3. **Conectar**:
   - Selecciona el servidor de la lista
   - Haz clic en "Conectar"

4. **Unirse a una Partida**:
   - Verás las partidas disponibles
   - Haz clic en una partida para seleccionarla
   - Haz clic en "Unirse a Partida"

5. **Iniciar la Partida**:
   - Haz clic en "Iniciar Partida"

6. **Grabar**:
   - Haz clic en "Iniciar Grabación"
   - La partida se grabará automáticamente
   - Haz clic en "Detener Grabación" cuando termines

### Ver Grabaciones

Las grabaciones se guardan en el directorio `recordings/`:
- `.json`: Formato legible con metadatos completos
- `.kr`: Formato binario Kaillera nativo

## Formato de Grabación

### Formato JSON

```json
{
  "recording_id": "20250303_180000",
  "timestamp": "2025-03-03T18:00:00",
  "server_host": "127.0.0.1",
  "server_port": 27888,
  "game_id": 1,
  "game_name": "Street Fighter II",
  "emulator": "MAME",
  "players": [...],
  "duration": 120.5,
  "frames": 7200,
  "frame_data": [...]
}
```

### Formato Kaillera (.kr)

Formato binario propietario compatible con emuladores Kaillera:
- Header: `KAI` (3 bytes)
- Versión: `0x01` (1 byte)
- Nombre del juego (32 bytes)
- Nombre del emulador (32 bytes)
- Timestamp (64 bytes)
- Game ID (4 bytes)
- Duración (4 bytes)
- Número de frames (4 bytes)
- Lista de jugadores
- Datos de cada frame

## Protocolo Kaillera

Este proyecto implementa el protocolo Kaillera 0.83:

- **Handshake**: `HELLO0.83` → `HELLOD00D[new_port]`
- **Login**: Envía información de usuario, emulador y tipo de conexión
- **ACK Exchange**: 4 paquetes para calcular ping
- **Join Game**: Se une a una sala existente
- **Start Game**: Inicia la sincronización de frames
- **Game Data**: Intercambio de datos de entrada en tiempo real

Más información en [Kaillera Protocol Documentation](https://kaillerareborn.github.io/resources/kailleraprotocol.txt)

## API REST

### Endpoints

- `GET /api/servers` - Lista servidores configurados
- `GET /api/instances` - Lista instancias activas
- `GET /api/recordings` - Lista grabaciones guardadas
- `POST /api/connect` - Conectar a un servidor
- `POST /api/disconnect` - Desconectar del servidor
- `POST /api/join-game` - Unirse a una partida
- `POST /api/leave-game` - Salir de una partida
- `POST /api/start-game` - Iniciar partida
- `POST /api/start-recording` - Iniciar grabación
- `POST /api/stop-recording` - Detener grabación
- `POST /api/delete-recording` - Eliminar grabación

## Desarrollo

### Estructura del Código

- `protocol/`: Implementación del protocolo Kaillera y cliente UDP
- `recorder/`: Sistema de grabación y exportación a diferentes formatos
- `api/`: Servidor HTTP con handlers para la API REST
- `frontend/`: Interfaz web en HTML/CSS/JavaScript

### Modificar el Puerto

Edita `backend/main.py`:
```python
run_server(host='0.0.0.0', port=8000)  # Cambia el puerto aquí
```

## Troubleshooting

### No puedo conectar al servidor
- Verifica que el servidor Kaillera esté corriendo
- Confirma el host y puerto correctos
- Verifica el firewall

### Las grabaciones no se guardan
- Asegúrate de tener permisos de escritura en el directorio `recordings/`
- Verifica que haya espacio en disco disponible

### Error de importación
- Asegúrate de ejecutar desde el directorio `backend/`
- Verifica que Python 3.7+ esté instalado

## Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Referencias

- [Kaillera Reborn](https://kaillerareborn.github.io) - Documentación y recursos
- [Kaillera Protocol](https://kaillerareborn.github.io/resources/kailleraprotocol.txt)
- [Direlera-rs](https://github.com/caromdreamer/direlera-rs) - Servidor Kaillera en Rust
- [Kaillera-Plus-Client](https://github.com/kwilson21/Kaillera-Plus-Client) - Cliente Kaillera en Python

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## Autor

Creado para la comunidad de Kaillera.

## Agradecimientos

- A la comunidad de [Kaillera Reborn](https://kaillerareborn.github.io) por el soporte y documentación
- A los autores del protocolo Kaillera original
- A todos los que contribuyen al ecosistema Kaillera
