# Diagnóstico de Conexión Kaillera

## Herramientas de Prueba

### 1. Prueba Simple

Esta es la herramienta más simple para probar la conexión:

```cmd
simple_test.bat
```

Esta herramienta:
- Crea un socket UDP
- Envía el mensaje HELLO: `HELLO0.83`
- Espera respuesta del servidor
- Muestra el resultado de forma clara

**Resultados esperados:**

✅ **Si funciona:**
```
[1] Creating UDP socket...
    ✓ Socket created
[2] Sending HELLO message...
    ✓ Sent: b'HELLO0.83'
[3] Waiting for response...
    ✓ Received X bytes from (...)
    ✓ Response: HELLOD00D7159
    ✓ Server responded with new port: 7159
    ✓ Connection test PASSED!
    ✓ Server is running Kaillera 0.83
```

❌ **Si falla (timeout):**
```
[1] Creating UDP socket...
    ✓ Socket created
[2] Sending HELLO message...
    ✓ Sent: b'HELLO0.83'
[ [3] Waiting for response (10s timeout)...
    ✗ TIMEOUT: No response from server

POSSIBLE REASONS:
   1. Server is NOT running on this port
   2. Firewall is blocking UDP packets
   3. Server port is different from 27888
   4. Network issue (cannot reach server)
```

### 2. Prueba de Versión

Prueba todas las versiones del protocolo Kaillera:

```cmd
cd backend
python simple_test.py kayinremix.duckdns.org 27888
python simple_test.py kayinremix.duckdns.org 27888 0.84
python simple_test.py kayinremix.duckdns.org 27888 0.85
```

Esto determinará qué versión del protocolo está usando el servidor.

## Diagnóstico Avanzado

### Si la prueba simple PASA pero el headless recorder FALLA:

#### Verificar Firewall en Windows

**Windows Firewall**
1. Panel de control → Windows Defender Firewall
2. Permite aplicación a través del firewall → Agregar o permitir
3. Agregar `python.exe` y permitir acceso completo
4. O desactiva temporalmente Windows Defender

**Regla de entrada**
1. Panel de control → Windows Defender → Firewall → Reglas de entrada y salida
2. Configuración avanzada → Reglas → Reglas de entrada → Nueva regla
3. Nombre: Kaillera
4. Tipo: Personaliza
5. Perfiles: Red pública y privada
6. Protocolo: UDP
7. Puertos remotos: 27888
8. Acciones: Permitir conexión
9. Habilitar: Permitir el paso de las redes

#### Verificar red
```cmd
ping kayinremix.duckdns.org
netstat -an | findstr 27888
```

### Verificar puerto del servidor

Pregunta al administrador del servidor:
- ¿El puerto es 27888?
- ¿Hay algún firewall en el servidor?
- ¿El servidor está usando EmuLinker-K o Direlera-rs?
- ¿El servidor está configurado para aceptar conexiones desde mi IP?

### Verificar que otros clientes pueden conectar

Descarga un cliente Kaillera real:
- MAME con Kaillera: https://www.nebula.org/files/kaillera/
- FBA con Kaillera: https://www.nebula.org/files/kaillera/
- Kawaks: http://kawaks.net/

Intenta conectar con ese cliente a `kayinremix.duckdns.org:27888`.

Si puedes conectar con otros clientes pero NO con mi headless recorder, entonces:
- El problema está en mi código
- Necesito corregir el protocolo

## Comprobaciones

### Paso 1: Ejecutar prueba simple

```cmd
cd C:\Users\Kayin\Documents\Test Grabador\headless-recorder-kaillera
simple_test.bat
```

### Paso 2: Analizar resultado

Si la prueba simple PASA:
- El servidor está funcionando correctamente
- El puerto 27888 está abierto
- El servidor usa Kaillera 0.83
- Mi código tiene un problema

Si la prueba simple FALLA (timeout):
- Verificar firewall
- Verificar que el servidor está corriendo
- Verificar que el puerto es 27888

### Paso 3: Reportar resultado

Por favor compárteme:
1. El resultado completo de `simple_test.bat`
2. Si el servidor está funcionando correctamente
3. Si puedes conectar con otros clientes Kaillera

Con esa información podré corregir el problema en mi código.

Esta herramienta:
- Crea un socket UDP
- Envía el mensaje HELLO: `HELLO0.83`
- Espera respuesta del servidor
- Muestra el resultado de forma clara

**Resultados esperados:**

✅ **Si funciona:**
```
Testing Kaillera Connection to kayinremix.duckdns.org:27888
============================================================
[1] Creating UDP socket...
    ✓ Socket created
[2] Sending HELLO message...
    ✓ Sent: b'HELLO0.83'
[3] Waiting for response (10s timeout)...
    ✓ Received X bytes from (...)
    ✓ Response: HELLOD00D7159
    ✓ Server responded with new port: 7159
    ✓ Connection test PASSED!
    ✓ Server is running Kaillera 0.83

============================================================
✓ TEST PASSED - You can connect to kaillera server!
 The headless recorder should work.
```

❌ **Si falla (timeout):**
```
Testing Kaillera Connection to kayinremix.duckdns.org:27888
============================================================
[1] Creating UDP socket...
    ✓ Socket created
[2] Sending HELLO message...
    ✓ Sent: b'HELLO0.83'
[3] Waiting for response (10s timeout)...
    ✗ TIMEOUT: No response from server

POSSIBLE REASONS:
   1. Server is NOT running on this port
   2. Firewall is blocking UDP packets
   3. Server port is different from 27888
   4. Network issue (cannot reach server)
```

❌ **Si el servidor responde TOO:**
```
✓ Server responded: TOO (server full or busy)
```

### 2. Prueba de Versiones

Prueba todas las versiones del protocolo Kaillera:

```cmd
cd backend
python simple_test.py kayinremix.duckdns.org 27888
python simple_test.py kayinremix.duckdns.org 27888 0.84
python simple_test.py kayinremix.duckdns.org 27888 0.85
```

Esto determinará qué versión del protocolo está usando el servidor.

## Diagnóstico Avanzado

Si la prueba simple PASA, pero el headless recorder FALLA:

### 1. Verificar Firewall en Windows

**Windows Firewall:**
1. Abre "Panel de control"
2. "Windows Defender Firewall" → "Permitir una aplicación a través del firewall"
3. "Permitir una aplicación → Permitir el acceso (private y public)"
4. Selecciona "python.exe" o tu script si está en otra ubicación
5. Click en "Permitir acceso"

**O crear regla de entrada:**
1. "Panel de control" → "Windows Defender Firewall"
2. "Reglas de entrada y salida" → "Nueva regla"
3. "Nombre": "Permitir Python UDP 27888"
4. "Tipo": "Personal"
5. "Acción": "Permitir conexión"
6. "Protocolos": "UDP"
7. "Puertos locales": "27888"

### 2. Verificar Red

**Ping:**
```cmd
ping kayinremix.duckdns.org
```

Deberías ver respuesta. Si no hay respuesta, hay un problema de red.

**Verificar puertos abiertos:**
```cmd
netstat -an | findstr :27888
```

Deberías ver algo como:
```
UDP    0.0.0.0:0         27888    *:*
```

### 3. Verificar que otros clientes Kaillera pueden conectar

Descarga un cliente Kaillera real:
- MAME con Kaillera: https://www.nebula.org/files/kaillera/
- FBA con Kaillera
- Kawaks: https://kawaks.net/downloads.php

Intenta conectar con `kayinremix.duckdns.org:27888`.

Si puedes conectar con otros clientes pero NO con mi headless recorder, entonces el problema está en mi código y lo corregiré.

Si NO puedes conectar con NINGÚN cliente, entonces el problema es del servidor (configuración, firewall, red, etc.).

## Comprobaciones

### ✅ Servidor funcionando

- [ ] El servidor EmuLinker-K está corriendo
- [ ] Otros clientes Kaillera pueden conectar

### ❌ Posibles problemas

1. **Firewall bloqueando puerto 27888 UDP**
   - Windows Firewall puede estar bloqueando
   - Asegúrate de permitir tráfico UDP en el puerto 27888
   - Prueba desactivando temporalmente el firewall

2. **El servidor está en un puerto diferente**
   - El puerto podría no ser 27888
   - EmuLinker-K por defecto usa:
     - Puerto principal: 27888 (control)
     - Puerto de juego: 8080 (datos)
   - Pregunta al administrador

3. **Problema de red**
   - La máquina no puede llegar al servidor
   - Router/firewall está bloqueando
   - DNS puede no estar resolviendo correctamente

4. **Configuración de EmuLinker-K**
   - Verificar `config/emulinker.cfg` en el servidor
   - El charset debe ser correcto (ej: Windows-1252)
   - Verificar que `controllers.connect.port=27888`

5. **El servidor está lleno o bloqueado**
   - EmuLinker-K puede tener límite de usuarios
   - Pregunta al administrador

## Pasos de Solución

### Paso 1: Ejecutar prueba simple

```cmd
cd C:\Users\Kayin\Documents\Test Grabador\headless-recorder-kaillera
simple_test.bat
```

### Paso 2: Analizar resultados

Si la prueba simple:
- **PASA**: El servidor está funcionando correctamente, el problema es en mi código. Reporta el resultado.
- **FALLA CON TIMEOUT**: Verifica firewall, red, y ejecuta comandos de diagnóstico
- **FALLA CON TOO**: El servidor está lleno o no aceptando más conexiones
- **FALLA CON OTRO**: El servidor responde algo diferente, necesita investigación

### Paso 3: Reportar resultado

Compárteme:
1. El resultado completo de `simple_test.bat`
2. Si otros clientes Kaillera pueden conectar
3. El resultado de `netstat -an | findstr :27888`
4. El resultado de `ping kayinremix.duckdns.org`

Con esa información podré identificar y corregir el problema.

## Comandos de Diagnóstico

### Prueba de puerto:
```cmd
netstat -an | findstr :27888
```

### Prueba de ping:
```cmd
ping kayinremix.duckdns.org
```

### Prueba de firewall:
```cmd
telnet kayinremix.duckdns.org 27888
```

## Sincronizar con Git

```cmd
cd C:\Users\Kayin\Documents\Test Grabador\headless-recorder-kaillera
git pull
```

## Estado Actual

Con la información de las herramientas de diagnóstico, podré identificar:

- ✅ El servidor está corriendo correctamente
- ✅ El puerto 27888 está abierto
- ✅ El servidor responde a HELLO0.83
- ✅ Otros clientes pueden conectar

## Próximos Pasos

1. Si la prueba simple PASA → El problema está en mi código del headless recorder
2. Si la prueba simple FALLA → El problema es del servidor o configuración
3. Basado en los resultados, corregiré el problema

Por favor, ejecuta `simple_test.bat` y compárteme el resultado completo.
