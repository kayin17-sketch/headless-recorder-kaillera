import json
import os
import sys
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Optional, List
import asyncio
from pathlib import Path


# Get the absolute path of this file
CURRENT_FILE = os.path.abspath(__file__)
# Go up 3 levels: backend/api/server.py -> backend/api -> backend -> project_root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_FILE)))
# Add project root to path
sys.path.insert(0, PROJECT_ROOT)

from protocol.kaillera_client import KailleraClient
from recorder.recorder import KailleraRecorder


class ServerManager:
    def __init__(self, servers_file: str):
        self.servers_file = servers_file
        self.servers: List[Dict] = []
        self._lock = threading.Lock()
        self._load_servers()
    
    def _load_servers(self):
        if not os.path.exists(self.servers_file):
            self.servers = []
            return
        
        try:
            with open(self.servers_file, 'r', encoding='utf-8') as f:
                self.servers = json.load(f)
        except Exception as e:
            print(f"Error loading servers: {e}")
            self.servers = []
    
    def _save_servers(self):
        try:
            with open(self.servers_file, 'w', encoding='utf-8') as f:
                json.dump(self.servers, f, indent=2)
        except Exception as e:
            print(f"Error saving servers: {e}")
    
    def get_servers(self) -> List[Dict]:
        with self._lock:
            return self.servers.copy()
    
    def add_server(self, name: str, host: str, port: int) -> Dict:
        server = {
            'id': f'server_{int(time.time() * 1000)}',
            'name': name,
            'host': host,
            'port': port
        }
        
        with self._lock:
            self.servers.append(server)
            self._save_servers()
        
        return server
    
    def delete_server(self, server_id: str) -> bool:
        with self._lock:
            initial_count = len(self.servers)
            self.servers = [s for s in self.servers if s['id'] != server_id]
            deleted = len(self.servers) < initial_count
            if deleted:
                self._save_servers()
        
        return deleted


class KailleraAPIHandler(BaseHTTPRequestHandler):
    instances: Dict[str, 'KailleraInstance'] = {}
    recorder = KailleraRecorder(os.path.join(PROJECT_ROOT, "recordings"))
    server_manager = ServerManager(os.path.join(PROJECT_ROOT, "backend", "servers.json"))
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        self.log_message("GET %s", parsed_path.path)
        
        if parsed_path.path == '/' or parsed_path.path == '/index.html':
            self.serve_static_file('frontend/templates/index.html', 'text/html')
        elif parsed_path.path == '/style.css':
            self.serve_static_file('frontend/static/style.css', 'text/css')
        elif parsed_path.path == '/app.js':
            self.serve_static_file('frontend/static/app.js', 'application/javascript')
        elif parsed_path.path == '/api/servers':
            self.handle_list_servers()
        elif parsed_path.path == '/api/instances':
            self.handle_list_instances()
        elif parsed_path.path.startswith('/api/recordings'):
            self.handle_list_recordings()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        self.log_message("POST %s", parsed_path.path)
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body.decode('utf-8'))
        except:
            data = {}
        
        if parsed_path.path == '/api/connect':
            self.handle_connect(data)
        elif parsed_path.path == '/api/disconnect':
            self.handle_disconnect(data)
        elif parsed_path.path == '/api/join-game':
            self.handle_join_game(data)
        elif parsed_path.path == '/api/leave-game':
            self.handle_leave_game(data)
        elif parsed_path.path == '/api/start-game':
            self.handle_start_game(data)
        elif parsed_path.path == '/api/start-recording':
            self.handle_start_recording(data)
        elif parsed_path.path == '/api/stop-recording':
            self.handle_stop_recording(data)
        elif parsed_path.path == '/api/delete-recording':
            self.handle_delete_recording(data)
        elif parsed_path.path == '/api/servers':
            self.handle_add_server(data)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_DELETE(self):
        parsed_path = urlparse(self.path)
        self.log_message("DELETE %s", parsed_path.path)
        
        # Extract server_id from path: /api/servers/{id}
        parts = parsed_path.path.split('/')
        if len(parts) == 4 and parts[1] == 'api' and parts[2] == 'servers':
            server_id = parts[3]
            self.handle_delete_server(server_id)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def serve_static_file(self, filepath: str, content_type: str):
        full_path = os.path.join(PROJECT_ROOT, filepath)
        full_path = os.path.normpath(full_path)
        
        self.log_message("Serving: %s", full_path)
        
        if not os.path.exists(full_path):
            self.log_message("File not found: %s", full_path)
            self.send_response(404)
            self.end_headers()
            return
        
        try:
            with open(full_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.log_message("Error reading file: %s", e)
            self.send_response(500)
            self.end_headers()
    
    def handle_list_servers(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        servers = self.server_manager.get_servers()
        self.wfile.write(json.dumps(servers).encode())
    
    def handle_add_server(self, data: dict):
        name = data.get('name')
        host = data.get('host')
        port = data.get('port')
        
        if not all([name, host, port]):
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Missing required fields: name, host, port'}).encode())
            return
        
        try:
            port = int(port)
        except (ValueError, TypeError):
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Port must be a number'}).encode())
            return
        
        server = self.server_manager.add_server(name, host, port)
        
        self.send_response(201)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(server).encode())
    
    def handle_delete_server(self, server_id: str):
        success = self.server_manager.delete_server(server_id)
        
        if success:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Server not found'}).encode())
    
    def handle_list_instances(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        instances = []
        for instance_id, instance in self.instances.items():
            instances.append({
                'id': instance_id,
                'connected': instance.client.connected,
                'server': instance.server,
                'current_game': instance.current_game
            })
        
        self.wfile.write(json.dumps(instances).encode())
    
    def handle_list_recordings(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        recordings = self.recorder.list_recordings()
        self.wfile.write(json.dumps(recordings).encode())
    
    def handle_connect(self, data: dict):
        instance_id = data.get('instance_id', 'default')
        host = data.get('host', '127.0.0.1')
        port = data.get('port', 27888)
        
        print(f"Connecting to {host}:{port}...")
        
        if instance_id in self.instances:
            print(f"Disconnecting existing instance {instance_id}")
            self.instances[instance_id].client.disconnect()
        
        client = KailleraClient()
        instance = KailleraInstance(instance_id, host, port, client)
        self.instances[instance_id] = instance
        
        def on_status_update(status):
            print(f"Status update: {status.users} users, {status.games} games")
            instance.update_status(status)
        
        def on_game_data(game_data):
            if instance.recording and instance.recorder:
                instance.recorder.add_frame(
                    len(instance.recorder.frame_data),
                    time.time(),
                    game_data.frame_data
                )
        
        client.on_status_update = on_status_update
        client.on_game_data = on_game_data
        
        # Run connection synchronously in handler
        try:
            print(f"Starting async connection...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(client.connect(host, port))
            print(f"Connection completed. Success: {success}")
            if success:
                print(f"Getting server status...")
                loop.run_until_complete(client.update_status(host))
            loop.close()
        except Exception as e:
            import traceback
            print(f"Connection error: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            success = False
        
        result = {
            'success': success,
            'connected': client.connected,
            'game_port': client.game_port
        }
        
        print(f"Sending response: {result}")
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
    
    def handle_disconnect(self, data: dict):
        instance_id = data.get('instance_id', 'default')
        
        if instance_id in self.instances:
            self.instances[instance_id].client.disconnect()
            del self.instances[instance_id]
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True}).encode())
    
    def handle_join_game(self, data: dict):
        instance_id = data.get('instance_id', 'default')
        game_id = data.get('game_id')
        
        if instance_id not in self.instances or game_id is None:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid request')
            return
        
        instance = self.instances[instance_id]
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(instance.client.join_game(instance.server['host'], game_id))
            instance.current_game = game_id
            loop.close()
        except Exception as e:
            print(f"Join game error: {e}")
            success = False
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'success': success}).encode())
    
    def handle_leave_game(self, data: dict):
        instance_id = data.get('instance_id', 'default')
        
        if instance_id in self.instances:
            self.instances[instance_id].current_game = None
            if self.instances[instance_id].recording:
                self.handle_stop_recording(data)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True}).encode())
    
    def handle_start_game(self, data: dict):
        instance_id = data.get('instance_id', 'default')
        
        if instance_id not in self.instances:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid request')
            return
        
        instance = self.instances[instance_id]
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(instance.client.start_game(instance.server['host']))
            loop.run_until_complete(instance.client.ready_to_play(instance.server['host']))
            loop.close()
        except Exception as e:
            print(f"Start game error: {e}")
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True}).encode())
    
    def handle_start_recording(self, data: dict):
        instance_id = data.get('instance_id', 'default')
        
        if instance_id not in self.instances:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid request')
            return
        
        instance = self.instances[instance_id]
        recording_id = self.recorder.start_recording(
            instance.server['host'],
            instance.server['port'],
            instance.current_game
        )
        instance.recording = True
        instance.recording_id = recording_id
        instance.recording_start_time = time.time()
        instance.recorder = KailleraRecorder()
        instance.recorder.start_recording(
            instance.server['host'],
            instance.server['port'],
            instance.current_game
        )
        instance.client.start_recording()
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'recording_id': recording_id}).encode())
    
    def handle_stop_recording(self, data: dict):
        instance_id = data.get('instance_id', 'default')
        
        if instance_id not in self.instances:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid request')
            return
        
        instance = self.instances[instance_id]
        instance.recording = False
        
        game_data = instance.client.stop_recording()
        duration = time.time() - instance.recording_start_time if hasattr(instance, 'recording_start_time') else 0
        
        if instance.recorder:
            recording = instance.recorder.stop_recording(duration)
            if recording:
                json_file = self.recorder.save_recording(recording)
                kr_file = self.recorder.save_kaillera_format(recording)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True}).encode())
    
    def handle_delete_recording(self, data: dict):
        recording_id = data.get('recording_id')
        
        if not recording_id:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid request')
            return
        
        success = self.recorder.delete_recording(recording_id)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'success': success}).encode())


class KailleraInstance:
    def __init__(self, instance_id: str, host: str, port: int, client: KailleraClient):
        self.instance_id = instance_id
        self.server = {'host': host, 'port': port}
        self.client = client
        self.current_game = None
        self.status = None
        self.recording = False
        self.recording_id = None
        self.recording_start_time = None
        self.recorder = None
    
    def update_status(self, status):
        self.status = status


def run_server(host: str = '0.0.0.0', port: int = 8000):
    print(f"CURRENT_FILE: {CURRENT_FILE}")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"Frontend path: {os.path.join(PROJECT_ROOT, 'frontend/templates/index.html')}")
    print(f"Servers file: {os.path.join(PROJECT_ROOT, 'backend/servers.json')}")
    server = HTTPServer((host, port), KailleraAPIHandler)
    print(f"Server running on http://{host}:{port}")
    server.serve_forever()


if __name__ == '__main__':
    run_server()
