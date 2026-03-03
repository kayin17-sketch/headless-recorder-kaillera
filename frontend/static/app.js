let servers = [];
let currentServer = null;
let connected = false;
let currentGame = null;
let recording = false;

document.addEventListener('DOMContentLoaded', function() {
    loadServers();
    loadRecordings();
    setInterval(updateStatus, 5000);
});

async function loadServers() {
    try {
        const response = await fetch('/api/servers');
        servers = await response.json();
        renderServers();
        updateServerSelect();
    } catch (error) {
        console.error('Error loading servers:', error);
    }
}

function renderServers() {
    const container = document.getElementById('servers-list');
    container.innerHTML = servers.map(server => `
        <div class="server-item">
            <h3>${server.name}</h3>
            <p>${server.host}:${server.port}</p>
            <div class="actions">
                <button onclick="removeServer('${server.id}')" class="danger">Eliminar</button>
            </div>
        </div>
    `).join('');
}

function updateServerSelect() {
    const select = document.getElementById('server-select');
    select.innerHTML = servers.map(server => 
        `<option value="${server.id}">${server.name} (${server.host}:${server.port})</option>`
    ).join('');
}

async function addServer() {
    const name = document.getElementById('server-name').value.trim();
    const host = document.getElementById('server-host').value.trim();
    const port = parseInt(document.getElementById('server-port').value);

    if (!name || !host || !port) {
        alert('Por favor, completa todos los campos');
        return;
    }

    const server = {
        id: 'server_' + Date.now(),
        name: name,
        host: host,
        port: port
    };

    servers.push(server);
    renderServers();
    updateServerSelect();

    document.getElementById('server-name').value = '';
    document.getElementById('server-host').value = '';
    document.getElementById('server-port').value = '';
}

function removeServer(serverId) {
    servers = servers.filter(s => s.id !== serverId);
    renderServers();
    updateServerSelect();
}

async function connect() {
    const serverId = document.getElementById('server-select').value;
    if (!serverId) {
        alert('Selecciona un servidor');
        return;
    }

    const server = servers.find(s => s.id === serverId);
    if (!server) return;

    currentServer = server;

    try {
        const response = await fetch('/api/connect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                instance_id: 'default',
                host: server.host,
                port: server.port
            })
        });

        const result = await response.json();
        
        if (result.success) {
            connected = true;
            updateConnectionStatus();
            loadGames();
        } else {
            alert('Error al conectar al servidor');
        }
    } catch (error) {
        console.error('Error connecting:', error);
        alert('Error al conectar al servidor');
    }
}

async function disconnect() {
    try {
        await fetch('/api/disconnect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ instance_id: 'default' })
        });

        connected = false;
        currentServer = null;
        currentGame = null;
        recording = false;
        
        updateConnectionStatus();
        document.getElementById('games-list').innerHTML = '';
    } catch (error) {
        console.error('Error disconnecting:', error);
    }
}

function updateConnectionStatus() {
    const statusEl = document.getElementById('connection-status');
    const connectBtn = document.getElementById('connect-btn');
    const disconnectBtn = document.getElementById('disconnect-btn');
    const joinBtn = document.getElementById('join-btn');
    const leaveBtn = document.getElementById('leave-btn');
    const startBtn = document.getElementById('start-btn');
    const recordBtn = document.getElementById('record-btn');

    if (connected) {
        statusEl.className = 'status connected';
        statusEl.textContent = 'Conectado a ' + currentServer.name;
        connectBtn.disabled = true;
        disconnectBtn.disabled = false;
        joinBtn.disabled = false;
    } else {
        statusEl.className = 'status disconnected';
        statusEl.textContent = 'Desconectado';
        connectBtn.disabled = false;
        disconnectBtn.disabled = true;
        joinBtn.disabled = true;
        leaveBtn.disabled = true;
        startBtn.disabled = true;
        recordBtn.disabled = true;
    }
}

async function loadGames() {
    const container = document.getElementById('games-list');
    container.innerHTML = '<p>Cargando partidas...</p>';

    setTimeout(() => {
        const mockGames = [
            { id: 1, name: 'Street Fighter II', emulator: 'MAME', players: '2/2', status: 0 },
            { id: 2, name: 'King of Fighters 97', emulator: 'MAME', players: '1/2', status: 0 },
            { id: 3, name: 'Marvel vs Capcom', emulator: 'FBA', players: '3/4', status: 1 }
        ];

        container.innerHTML = mockGames.map(game => `
            <div class="game-item" data-game-id="${game.id}" onclick="selectGame(${game.id})">
                <h3>${game.name}</h3>
                <p>${game.emulator} - ${game.players} - ${game.status === 0 ? 'Esperando' : 'Jugando'}</p>
            </div>
        `).join('');
    }, 500);
}

function selectGame(gameId) {
    document.querySelectorAll('.game-item').forEach(el => el.classList.remove('selected'));
    const selected = document.querySelector(`.game-item[data-game-id="${gameId}"]`);
    if (selected) {
        selected.classList.add('selected');
        currentGame = gameId;
        document.getElementById('start-btn').disabled = false;
        document.getElementById('record-btn').disabled = false;
    }
}

async function joinGame() {
    if (!currentGame) {
        alert('Selecciona una partida primero');
        return;
    }

    try {
        const response = await fetch('/api/join-game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                instance_id: 'default',
                game_id: currentGame
            })
        });

        const result = await response.json();
        
        if (result.success) {
            document.getElementById('leave-btn').disabled = false;
            alert('Te has unido a la partida');
        } else {
            alert('Error al unirse a la partida');
        }
    } catch (error) {
        console.error('Error joining game:', error);
        alert('Error al unirse a la partida');
    }
}

async function leaveGame() {
    try {
        await fetch('/api/leave-game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ instance_id: 'default' })
        });

        currentGame = null;
        document.getElementById('leave-btn').disabled = true;
        document.getElementById('start-btn').disabled = true;
        
        if (recording) {
            stopRecording();
        }

        document.querySelectorAll('.game-item').forEach(el => el.classList.remove('selected'));
    } catch (error) {
        console.error('Error leaving game:', error);
    }
}

async function startGame() {
    if (!currentGame) {
        alert('Selecciona una partida primero');
        return;
    }

    try {
        const response = await fetch('/api/start-game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ instance_id: 'default' })
        });

        const result = await response.json();
        
        if (result.success) {
            alert('Partida iniciada. Puedes comenzar a grabar.');
        } else {
            alert('Error al iniciar la partida');
        }
    } catch (error) {
        console.error('Error starting game:', error);
        alert('Error al iniciar la partida');
    }
}

async function startRecording() {
    if (!connected || !currentGame) {
        alert('Debes estar conectado y en una partida para grabar');
        return;
    }

    try {
        const response = await fetch('/api/start-recording', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ instance_id: 'default' })
        });

        const result = await response.json();
        
        if (result.recording_id) {
            recording = true;
            updateRecordingStatus(result.recording_id);
        }
    } catch (error) {
        console.error('Error starting recording:', error);
        alert('Error al iniciar la grabación');
    }
}

async function stopRecording() {
    if (!recording) return;

    try {
        await fetch('/api/stop-recording', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ instance_id: 'default' })
        });

        recording = false;
        updateRecordingStatus(null);
        loadRecordings();
    } catch (error) {
        console.error('Error stopping recording:', error);
        alert('Error al detener la grabación');
    }
}

function updateRecordingStatus(recordingId) {
    const statusEl = document.getElementById('recording-status');
    const recordBtn = document.getElementById('record-btn');
    const stopBtn = document.getElementById('stop-btn');

    if (recording) {
        statusEl.className = 'status recording';
        statusEl.textContent = 'Grabando... ID: ' + (recordingId || 'Desconocido');
        recordBtn.disabled = true;
        stopBtn.disabled = false;
    } else {
        statusEl.className = 'status';
        statusEl.textContent = 'No grabando';
        recordBtn.disabled = false;
        stopBtn.disabled = true;
    }
}

async function loadRecordings() {
    try {
        const response = await fetch('/api/recordings');
        const recordings = await response.json();
        renderRecordings(recordings);
    } catch (error) {
        console.error('Error loading recordings:', error);
    }
}

function renderRecordings(recordings) {
    const container = document.getElementById('recordings-list');
    
    if (recordings.length === 0) {
        container.innerHTML = '<p>No hay grabaciones guardadas</p>';
        return;
    }

    container.innerHTML = recordings.map(rec => `
        <div class="recording-item">
            <div class="info">
                <h3>${rec.game_name || 'Partida ' + rec.recording_id}</h3>
                <p>ID: ${rec.recording_id} | Duración: ${Math.round(rec.duration)}s | Frames: ${rec.frames}</p>
                <p>Servidor: ${rec.server_host}:${rec.server_port} | ${rec.timestamp}</p>
            </div>
            <div class="actions">
                <button onclick="deleteRecording('${rec.recording_id}')" class="danger">Eliminar</button>
            </div>
        </div>
    `).join('');
}

async function deleteRecording(recordingId) {
    if (!confirm('¿Estás seguro de eliminar esta grabación?')) return;

    try {
        await fetch('/api/delete-recording', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ recording_id: recordingId })
        });

        loadRecordings();
    } catch (error) {
        console.error('Error deleting recording:', error);
        alert('Error al eliminar la grabación');
    }
}

async function updateStatus() {
    if (!connected) return;

    try {
        const response = await fetch('/api/instances');
        const instances = await response.json();

        const instance = instances.find(i => i.id === 'default');
        if (instance && !instance.connected) {
            connected = false;
            updateConnectionStatus();
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}
