# Guía de Instalación para Windows

Esta guía explica cómo instalar y ejecutar el Kaillera Headless Recorder en Windows.

## Requisitos

- Windows 10/11
- Python 3.7 o superior

## Instalación de Python en Windows

1. Descarga Python desde [python.org](https://www.python.org/downloads/)
2. Durante la instalación, **importante**: marca la casilla "Add Python to PATH"
3. Completa la instalación

Verifica la instalación:
```cmd
python --version
```

## Instalación del Proyecto

### Opción 1: Descargar desde GitHub

1. Ve a [https://github.com/kayin17-sketch/headless-recorder-kaillera](https://github.com/kayin17-sketch/headless-recorder-kaillera)
2. Haz clic en "Code" → "Download ZIP"
3. Descomprime el archivo en una carpeta de tu elección

### Opción 2: Usar Git

Si tienes Git instalado:
```cmd
git clone https://github.com/kayin17-sketch/headless-recorder-kaillera.git
cd headless-recorder-kaillera
```

## Ejecutar el Servidor

### Método Recomendado: Doble Click

1. Abre la carpeta del proyecto en el Explorador de Archivos
2. Haz doble click en `start.bat`
3. Se abrirá una ventana de comando y el servidor se iniciará

### Método Alternativo: Línea de Comandos

1. Abre el Símbolo del Sistema (cmd) o PowerShell
2. Navega a la carpeta del proyecto:
```cmd
cd C:\ruta\a\headless_recorder_kaillera
```

3. Ejecuta el script:
```cmd
start.bat
```

O directamente:
```cmd
cd backend
python main.py
```

## Acceder a la Interfaz Web

Una vez iniciado el servidor, abre tu navegador y visita:
```
http://localhost:8000
```

## Uso Básico

1. **Configurar Servidor:**
   - Nombre: EmuLinker-K
   - Host: IP del servidor (ej: 192.168.1.100)
   - Puerto: 27888 (o el puerto que configure EmuLinker-K)

2. **Conectar:** Haz clic en "Conectar"

3. **Unirse a Partida:** Selecciona una partida y haz clic en "Unirse a Partida"

4. **Grabar:** Haz clic en "Iniciar Grabación"

## Configurar Firewall de Windows

La primera vez que ejecutes el programa, Windows puede mostrar una alerta de firewall:

- Selecciona "Permitir acceso"
- Asegúrate de marcar ambas opciones (red privada y pública si necesitas acceso externo)

## Solución de Problemas Comunes

### "python no se reconoce como un comando interno"

Esto significa que Python no está en el PATH:

1. reinstala Python asegurándote de marcar "Add Python to PATH"
2. O añádelo manualmente:
   - Presiona Win + X → Sistema → Configuración avanzada del sistema
   - Variables de entorno → Variables del sistema → Path → Editar
   - Añade: `C:\Users\tu_usuario\AppData\Local\Programs\Python\Python3x\` y `C:\Users\tu_usuario\AppData\Local\Programs\Python\Python3x\Scripts\`

### El servidor no inicia en el puerto 8000

Cambia el puerto en `backend/main.py`:
```python
run_server(host='0.0.0.0', port=8080)  # Cambiar a 8080
```

### No puedo conectarme al servidor EmuLinker-K

1. Verifica que EmuLinker-K esté corriendo
2. Verifica la dirección IP y puerto
3. Desactiva temporalmente el firewall para probar
4. Si está en otra máquina, verifica que puedan comunicarse:
   ```cmd
   ping 192.168.1.100
   ```

### Las grabaciones no se guardan

Verifica que tienes permisos de escritura en la carpeta:
1. Ejecuta el script como Administrador (click derecho → Ejecutar como administrador)
2. O mueve la carpeta del proyecto a tu carpeta de usuario o Documentos

## Configurar para Acceso desde Otras Máquinas

Para acceder a la interfaz web desde otros dispositivos en tu red:

1. Encuentra tu IP local:
   ```cmd
   ipconfig
   ```
   Busca la dirección IPv4 (ej: 192.168.1.50)

2. Asegúrate de que el servidor use `0.0.0.0` como host (ya está configurado así)

3. Permite el puerto en el Firewall:
   - Windows Defender → Firewall con seguridad avanzada
   - Reglas de entrada → Nueva regla
   - Puerto → TCP → 8000 → Permitir conexión

4. Accede desde otra máquina:
   ```
   http://192.168.1.50:8000
   ```

## Ejecutar como Servicio (Opcional)

Para ejecutar automáticamente al iniciar Windows:

1. Descarga NSSM (Non-Sucking Service Manager): https://nssm.cc/download
2. Extrae y ejecuta `nssm.exe` como Administrador
3. Menu → Install service:
   - Path: `C:\Python39\python.exe`
   - Startup directory: `C:\ruta\a\headless_recorder_kaillera\backend`
   - Arguments: `main.py`
4. Haz clic en "Install service"

## Rutas de Archivos Importantes

- Grabaciones: `C:\ruta\a\headless_recorder_kaillera\recordings\`
- Configuración: `C:\ruta\a\headless_recorder_kaillera\config.yaml`
- Servidor: `C:\ruta\a\headless_recorder_kaillera\backend\main.py`
- Scripts de inicio:
  - Windows: `start.bat`
  - Linux/Mac: `start.sh`

## Actualizar el Proyecto

Si clonaste con Git:
```cmd
git pull
```

Si descargaste el ZIP:
1. Descarga la nueva versión
2. Copia el directorio `recordings/` a la nueva carpeta (para conservar tus grabaciones)
3. Borra la versión antigua

## Características Específicas de Windows

✅ **Socket UDP**: Compatible con el protocolo Kaillera
✅ **HTTP Server**: Funciona con el servidor http.server de Python
✅ **File System**: Usa `os.path` para compatibilidad cross-platform
✅ **Encoding**: Soporte completo para archivos .kr (binario) y JSON
✅ **AsyncIO**: Funciona correctamente en Python 3.7+ en Windows

## Soporte

Si encuentras problemas:

1. Revisa el archivo `EXAMPLES.md` para más ejemplos
2. Revisa el archivo `README.md` para documentación general
3. Abre un issue en: https://github.com/kayin17-sketch/headless-recorder-kaillera/issues

## Recursos Adicionales

- [Python para Windows](https://docs.python.org/3/using/windows.html)
- [EmuLinker-K](https://github.com/hopskipnfall/EmuLinker-K)
- [Kaillera Reborn](https://kaillerareborn.github.io)
